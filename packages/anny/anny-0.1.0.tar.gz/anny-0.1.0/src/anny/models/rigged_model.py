# Anny
# Copyright (C) 2025 NAVER Corp.
# Apache License, Version 2.0
import torch
import anny.utils.kinematics as kinematics
import anny.skinning.skinning as skinning
from anny.utils.mesh_utils import triangulate_faces
import roma
import warnings

def _get_pose_parameterization_with_identity_root_delta_transform(rest_bone_poses, delta_transform, base_transform):
        rest_root_bone_pose = rest_bone_poses[...,0,:,:]
        identity = torch.eye(4, dtype=rest_bone_poses.dtype, device=rest_bone_poses.device)[None]
        output_base_transform = rest_root_bone_pose @ delta_transform[...,0,:,:] @ roma.Rigid.from_homogeneous(rest_root_bone_pose).inverse().to_homogeneous()
        if base_transform is not None:
            output_base_transform = base_transform @ output_base_transform
        output_delta_transform = delta_transform.clone()
        output_delta_transform[...,0,:,:] = identity
        return output_delta_transform, output_base_transform

def _get_pose_parameterization_with_identity_base_transform(rest_bone_poses, delta_transform, base_transform):
    if base_transform is None:
        return delta_transform, None
    output_delta_transform = delta_transform.clone()
    rest_root_bone_pose = rest_bone_poses[...,0,:,:]
    output_delta_transform[...,0,:,:] = roma.Rigid.from_homogeneous(rest_root_bone_pose).inverse().to_homogeneous() @ base_transform @ rest_root_bone_pose @ delta_transform[...,0,:,:]
    return output_delta_transform, None

def _get_pose_parameterization_with_translation_only_base_transform(rest_bone_poses, delta_transform, base_transform):
    """
    Return a pose parametrization ensuring that the root delta_transform is a pure rotation, and that base_transform is a pure translation.
    """
    rest_root_bone_pose = roma.Rigid.from_homogeneous(rest_bone_poses[...,0,:,:])
    input_root_delta_transform = roma.Rigid.from_homogeneous(delta_transform[...,0,:,:])
    if base_transform is None:
        batch_shape = rest_root_bone_pose.linear.shape[:-2]
        base_transform = roma.Rigid.Identity(3, batch_shape, dtype=rest_bone_poses.dtype, device=rest_bone_poses.device)
    else:
        base_transform = roma.Rigid.from_homogeneous(base_transform)
    # Move the base transform into the root delta transform
    temp_root_delta_transform = rest_root_bone_pose.inverse() @ base_transform @ rest_root_bone_pose @ input_root_delta_transform
    # Move back the translation part into the base transform
    output_root_delta_transform = roma.Rigid(temp_root_delta_transform.linear, None)
    output_base_transform = rest_root_bone_pose @ roma.Rigid(None, temp_root_delta_transform.translation) @ rest_root_bone_pose.inverse()

    output_delta_transform = delta_transform.clone()
    output_delta_transform[...,0,:,:] = output_root_delta_transform.to_homogeneous()
    output_base_transform = output_base_transform.to_homogeneous()
    return output_delta_transform, output_base_transform

class RiggedModelWithLinearBlendShapes(torch.nn.Module):
    def __init__(self,
                 template_vertices,
                 faces,
                 texture_coordinates,
                 face_texture_coordinate_indices,
                 blendshapes,
                 template_bone_heads,
                 bone_heads_blendshapes,
                 template_bone_tails,
                 bone_tails_blendshapes,
                 bone_rolls_rotmat,
                 bone_parents,
                 bone_labels,
                 vertex_bone_weights,
                 vertex_bone_indices,
                 skinning_method : str = None,
                 default_pose_parameterization : str = "root_relative_world"):
        super().__init__()
        self.register_buffer("template_vertices", template_vertices, persistent=False)
        self.faces = faces
        self.register_buffer("texture_coordinates", texture_coordinates, persistent=False)
        self.register_buffer("face_texture_coordinate_indices", face_texture_coordinate_indices, persistent=False)
        self.register_buffer("blendshapes", blendshapes, persistent=False)
        self.register_buffer("template_bone_heads", template_bone_heads, persistent=False)
        self.register_buffer("bone_heads_blendshapes", bone_heads_blendshapes, persistent=False)
        self.register_buffer("template_bone_tails", template_bone_tails, persistent=False)
        self.register_buffer("bone_tails_blendshapes", bone_tails_blendshapes, persistent=False)
        self.register_buffer("y_axis", torch.as_tensor([0.,1.,0.], dtype=self.template_vertices.dtype), persistent=False)
        self.register_buffer("degenerate_rotation", torch.tensor([[1.,0.,0.],[0.,-1.,0.],[0.,0.,-1.]], dtype=self.template_vertices.dtype), persistent=False)
        self.register_buffer("bone_rolls_rotmat", bone_rolls_rotmat, persistent=False)
        self.bone_parents = bone_parents
        self.kinematic_propagation_fronts = kinematics.get_kinematic_propagation_fronts(bone_parents)
        self.bone_labels = bone_labels
        self.register_buffer("vertex_bone_weights", vertex_bone_weights, persistent=False)
        self.register_buffer("vertex_bone_indices", vertex_bone_indices, persistent=False)
        self.set_skinning_method(skinning_method)
        self.default_pose_parameterization = default_pose_parameterization


    @property
    def bone_count(self):
        return len(self.bone_labels)

    @property
    def dtype(self):
        return self.template_vertices.dtype

    @property
    def device(self):
        return self.template_vertices.device
    
    def get_triangular_faces(self):
        """
        Return a triangulated version of the faces, splitting quads when needed.
        """
        triangular_faces = torch.tensor(triangulate_faces(vertices=self.template_vertices, faces=self.faces.detach().cpu().numpy().tolist()), device=self.device)
        return triangular_faces

    def set_skinning_method(self, skinning_method):
        if skinning_method is None:
            # Default skinning settings.
            try:
                import anny.skinning.warp_skinning
                skinning_method = "warp_lbs"
            except ImportError:
                warnings.warn("Fallback to default lbs skinning. Consider installing NVidia Warp for lower memory footprint.")
                skinning_method = "lbs"
        if skinning_method == "lbs":
            self._skinning_method = skinning.linear_blend_skinning
        elif skinning_method == "dqs":
            self._skinning_method = skinning.dual_quaternion_skinning
        elif skinning_method == "warp_lbs":
            import anny.skinning.warp_skinning
            self._skinning_method = lambda vertices, bone_weights, bone_indices, bone_transforms : anny.skinning.warp_skinning.linear_blend_skinning(vertices, bone_weights.squeeze(dim=0), bone_indices.squeeze(dim=0), bone_transforms)
        else:
            raise NotImplementedError

    def get_rest_bone_poses(self, blendshape_coeffs):
        rest_bone_heads = skinning.apply_linear_blendshape(self.template_bone_heads, self.bone_heads_blendshapes, blendshape_coeffs)
        rest_bone_tails = skinning.apply_linear_blendshape(self.template_bone_tails, self.bone_tails_blendshapes, blendshape_coeffs)
        rest_bone_poses = kinematics.get_bone_poses(rest_bone_heads, rest_bone_tails, self.bone_rolls_rotmat, y_axis=self.y_axis, degenerate_rotation=self.degenerate_rotation)
        return rest_bone_heads, rest_bone_tails, rest_bone_poses

    def get_rest_vertices(self, blendshape_coeffs):
        return skinning.apply_linear_blendshape(self.template_vertices, self.blendshapes, blendshape_coeffs)
    
    def parse_delta_transforms_dict(self, delta_transforms_dict, batch_size=None):
        """
        Converts a dictionary, namedtuple, or tensor representation of delta transforms
        into a batched tensor of homogeneous transformation matrices.

        This function supports the following input formats:
        - A `dict` or `namedtuple` mapping `bone_label` strings to per-bone delta transforms
        (either `torch.Tensor` or `roma.Rigid` objects), where each transform is of shape `(B, 4, 4)`.
        - A full `torch.Tensor` of shape `(B, N, 4, 4)` representing the full batch of transforms.

        Any bones missing from the input dict/namedtuple are automatically filled with identity transforms.

        Args:
            delta_transforms_dict (dict | namedtuple | torch.Tensor):
                A dictionary or namedtuple mapping bone labels (from `self.bone_labels`)
                to delta transform tensors or `roma.Rigid` objects of shape `(B, 4, 4)`,
                or a tensor of shape `(B, N, 4, 4)` representing the full batch directly.

        Returns:
            torch.Tensor: A tensor of shape `(B, N, 4, 4)`, where `B` is the batch size and
                        `N` is the number of joints (length of `self.bone_labels`), representing
                        the batched homogeneous transformation matrices.

        Raises:
            NameError: If `delta_transforms_dict` is not a supported type.
            AssertionError: If any provided transform does not have the expected shape `(B, 4, 4)`.
        """

        if isinstance(delta_transforms_dict, tuple) and hasattr(delta_transforms_dict, '_fields'):
            delta_transforms_dict = delta_transforms_dict._asdict()

        if isinstance(delta_transforms_dict, dict):
            batch_size = batch_size if batch_size is not None else len(next(iter(delta_transforms_dict.values())))
            identity = torch.eye(4, dtype=self.template_vertices.dtype, device=self.template_vertices.device)[None].repeat(batch_size, 1, 1)
            delta_transforms = []
            for bone_id, bone_label in enumerate(self.bone_labels):
                if bone_label in delta_transforms_dict:
                    delta = delta_transforms_dict[bone_label]
                    if isinstance(delta, roma.Rigid):
                        delta = delta.to_homogeneous()
                    assert delta.shape == (batch_size, 4, 4), f"Invalid shape {delta.shape} for bone '{bone_label}'"
                else:
                    delta = identity
                delta_transforms.append(delta)
            return torch.stack(delta_transforms, dim=1)
        
        elif delta_transforms_dict is None:
            identity = torch.eye(4, dtype=self.template_vertices.dtype, device=self.template_vertices.device)[None].repeat(batch_size, len(self.bone_labels), 1, 1)
            return identity
        
        elif isinstance(delta_transforms_dict, torch.Tensor):
            return delta_transforms_dict
        
        else:
            raise NameError(f"delta_transforms_dict should be a dict, a namedtuple or a tensor, but got {type(delta_transforms_dict)}")
            
    def get_bone_poses(self, rest_bone_poses, delta_transforms, base_transform=None):
        """
        Args:
            - base_transform (None or batch_sizex4x4 homogeneous transform)
        """
        delta_transforms = self.parse_delta_transforms_dict(delta_transforms)
        return kinematics.parallel_forward_kinematic(self.kinematic_propagation_fronts, rest_bone_poses, delta_transforms, base_transform)
    
    def get_bone_ends(self, rest_bone_heads, rest_bone_tails, rest_bone_poses, bone_poses):
        relative_transform = roma.Rigid.from_homogeneous(bone_poses) @ roma.Rigid.from_homogeneous(rest_bone_poses).inverse()
        bone_heads = relative_transform.apply(rest_bone_heads)
        bone_tails = relative_transform.apply(rest_bone_tails)
        return bone_heads, bone_tails

    def get_skinned_vertices(self, rest_vertices, bone_transforms):
        """
        Args:
            - rest_vertices: BxVx3
            - bone_transforms: list of J batch of transformations
        """
        if isinstance(bone_transforms, list) and isinstance(bone_transforms[0], roma.Rigid):
            bone_transforms = roma.Rigid(torch.stack([t.linear for t in bone_transforms], dim=1), torch.stack([t.translation for t in bone_transforms], dim=1))
            bone_transforms = bone_transforms.to_homogeneous()
        elif isinstance(bone_transforms, torch.Tensor):
            pass
        vertices = self._skinning_method(rest_vertices,
                                        bone_weights=self.vertex_bone_weights.unsqueeze(dim=0),
                                        bone_indices=self.vertex_bone_indices.unsqueeze(dim=0),
                                        bone_transforms=bone_transforms)    
        return vertices
    
    def forward(self, pose_parameters, blendshape_coeffs, pose_parameterization=None, return_bone_ends=False):
        """
        Helper function to compute the skinned vertices and bone poses.
        Args:
            - pose_parameters: BxJx4x4
            - blendshape_coeffs: BxN
        Returns:
            - A dictionary with:
                - blendshape_coeffs: BxN
                - vertices: BxVx3
                - bone_poses: BxJx4x4
        """
        rest_bone_heads, rest_bone_tails, rest_bone_poses = self.get_rest_bone_poses(blendshape_coeffs)
        pose_parameterization = self.default_pose_parameterization if (pose_parameterization is None) else pose_parameterization
        delta_transforms = self.parse_delta_transforms_dict(pose_parameters, batch_size=blendshape_coeffs.shape[0])
        if pose_parameterization == "root_relative":
            # The first pose parameter describes the pose of the root bone
            base_transform = roma.Rigid.from_homogeneous(rest_bone_poses[:,0,:,:]).inverse().to_homogeneous()
        elif pose_parameterization == "rest_relative":
            # All parameters are relative to the rest pose
            base_transform = None
        elif pose_parameterization == "root_relative_world":
            # The translation part of the first pose parameter describes the location of the root joint.
            # The rotation part is left-applied to the rest orientation of the root bone.
            rest_root_pose = roma.Rigid.from_homogeneous(rest_bone_poses[:,0,:,:])
            base_transform = rest_root_pose.inverse().to_homogeneous()
            root_param = delta_transforms[:,0]
            delta_transforms = delta_transforms.clone()
            delta_transforms[:,0] = root_param @ roma.Rigid(rest_root_pose.linear, translation=None).to_homogeneous()
        elif pose_parameterization == "absolute":
            bone_poses = delta_transforms
            rest_bone_poses_inverse = roma.Rigid.from_homogeneous(rest_bone_poses).inverse().to_homogeneous()
            bone_transforms = bone_poses @ rest_bone_poses_inverse
            parent_bone_transforms = bone_transforms[:, self.bone_parents, :, :]
            parent_bone_transforms[:, 0, :, :] = torch.eye(4, dtype=self.template_vertices.dtype, device=self.template_vertices.device)[None]
            delta_transforms = rest_bone_poses_inverse @ roma.Rigid.from_homogeneous(parent_bone_transforms).inverse().to_homogeneous() @ bone_poses
            base_transform = None
        else:
            raise NotImplementedError(f"Pose parametrization {pose_parameterization} not implemented")
        
        if pose_parameterization != "absolute":
            bone_poses, bone_transforms = self.get_bone_poses(rest_bone_poses=rest_bone_poses, delta_transforms=delta_transforms, base_transform=base_transform)

        rest_vertices = self.get_rest_vertices(blendshape_coeffs)
        vertices = self.get_skinned_vertices(bone_transforms=bone_transforms, rest_vertices=rest_vertices)
        output = dict(blendshape_coeffs=blendshape_coeffs,
                    rest_vertices=rest_vertices,
                    vertices=vertices,
                    bone_poses=bone_poses,
                    rest_bone_heads=rest_bone_heads,
                    rest_bone_tails=rest_bone_tails,
                    rest_bone_poses=rest_bone_poses,
                    delta_transforms=delta_transforms,
                    base_transform=base_transform)
        if return_bone_ends:
            bone_heads, bone_tails = self.get_bone_ends(rest_bone_heads, rest_bone_tails, rest_bone_poses, bone_poses)
            output["bone_heads"] = bone_heads
            output["bone_tails"] = bone_tails
        return output
    
    def get_pose_parameterization(self,
                                model_output,
                                target_pose_parameterization):
        
        if target_pose_parameterization == "rest_relative":
            delta_transform, base_transform = _get_pose_parameterization_with_identity_base_transform(rest_bone_poses=model_output["rest_bone_poses"],
                                                                  delta_transform=model_output["delta_transforms"],
                                                                  base_transform=model_output["base_transform"])
            return delta_transform
        elif target_pose_parameterization == "root_relative":
            # The first pose parameter describes the pose of the root bone
            pose_parameters = model_output["delta_transforms"].clone()
            pose_parameters[:,0] = model_output["bone_poses"][:,0]
            return pose_parameters
        elif target_pose_parameterization == "root_relative_world":
            # The translation part of the first pose parameter describes the location of the root joint.
            # The rotation part is left-applied to the rest orientation of the root bone.
            root_pose = roma.Rigid.from_homogeneous(model_output["bone_poses"][:,0])
            rot = root_pose.linear @ roma.Rigid.from_homogeneous(model_output["rest_bone_poses"][:,0]).linear.inverse()
            pose_parameters = model_output["delta_transforms"].clone()
            pose_parameters[:,0] = roma.Rigid(rot, root_pose.translation).to_homogeneous()
            return pose_parameters
        elif target_pose_parameterization == "absolute":
            return model_output["bone_poses"]
        else:
            raise NotImplementedError(f"Pose parametrization {target_pose_parameterization} not implemented")