import torch
import anny
import roma
import unittest
import anny.models.rigged_model

class TestPoseParametrization(unittest.TestCase):
    def test_pose_parameterization_conversions(self):
        dtype = torch.float64
        model = anny.create_fullbody_model().to(dtype=dtype)

        batch_size = 32
        phenotype_kwargs = {key : torch.rand(batch_size, dtype=dtype) for key in model.phenotype_labels}
        source_pose_parameters = roma.Rigid(roma.random_rotmat((batch_size, model.bone_count), dtype=dtype), torch.randn((batch_size, model.bone_count, 3), dtype=dtype)).to_homogeneous()

        parametrization_list = ["rest_relative", "root_relative", "root_relative_world", "absolute"]

        for source_pose_parameterization in parametrization_list:
            source_output = model(pose_parameters=source_pose_parameters,
                    phenotype_kwargs=phenotype_kwargs,
                    pose_parameterization=source_pose_parameterization)
        
            for target_pose_parameterization in parametrization_list:
                target_pose_parameters = model.get_pose_parameterization(source_output, target_pose_parameterization=target_pose_parameterization)
                target_output = model(pose_parameters=target_pose_parameters,
                        phenotype_kwargs=phenotype_kwargs,
                        pose_parameterization=target_pose_parameterization)
                self.assertTrue(torch.allclose(source_output["vertices"], target_output["vertices"], atol=1e-5), f"Pose parametrization conversion error from {source_pose_parameterization} to {target_pose_parameterization}")


    def test_reparametrization(self):
        batch_size = 32
        dtype = torch.float64
        device = torch.device('cpu')
        model = anny.create_fullbody_model().to(dtype=dtype, device=device)
        
        torch.use_deterministic_algorithms(True)

        generator = None
        phenotype_kwargs = dict(gender=torch.rand((batch_size,), dtype=dtype, device=device, generator=generator),
                                age=torch.rand((batch_size,), dtype=dtype, device=device, generator=generator),
                                muscle=torch.rand((batch_size,), dtype=dtype, device=device, generator=generator),
                                weight=torch.rand((batch_size,), dtype=dtype, device=device, generator=generator),
                                height=torch.rand((batch_size,), dtype=dtype, device=device, generator=generator),
                                proportions=torch.rand((batch_size,), dtype=dtype, device=device, generator=generator),
                                cupsize=torch.rand((batch_size,), dtype=dtype, device=device, generator=generator),
                                firmness=torch.rand((batch_size,), dtype=dtype, device=device, generator=generator),
                                african=torch.rand((batch_size,), dtype=dtype, device=device, generator=generator),
                                asian=torch.rand((batch_size,), dtype=dtype, device=device, generator=generator),
                                caucasian=torch.rand((batch_size,), dtype=dtype, device=device, generator=generator))
        
        blendshape_coeffs = model.get_phenotype_blendshape_coefficients(**phenotype_kwargs)
        rest_vertices = model.get_rest_vertices(blendshape_coeffs)
        rest_bone_heads, rest_bone_tails, rest_bone_poses = model.get_rest_bone_poses(blendshape_coeffs)

        base_transform0 = roma.Rigid(roma.random_rotmat(batch_size, dtype=dtype, device=device), torch.randn((batch_size, 3), dtype=dtype, device=device)).to_homogeneous()
        delta_transforms0 = roma.Rigid(roma.random_rotmat((batch_size, model.bone_count), dtype=dtype, device=device),
                                        torch.randn((batch_size, model.bone_count, 3), dtype=dtype, device=device)).to_homogeneous()
        bone_poses0, bone_transforms0 = model.get_bone_poses(rest_bone_poses, delta_transforms0, base_transform0)

        delta_transforms1, base_transform1 = anny.models.rigged_model._get_pose_parameterization_with_identity_root_delta_transform(rest_bone_poses, delta_transforms0, base_transform0)
        self.assertTrue(torch.all(delta_transforms1[:,0,:,:] - torch.eye(4, dtype=dtype, device=device)[None] == 0.))
        bone_poses1, bone_transforms1 = model.get_bone_poses(rest_bone_poses, delta_transforms1, base_transform1)
        self.assertTrue(torch.all(torch.abs(bone_poses0 - bone_poses1) < 1e-6))
        self.assertTrue(torch.all(torch.abs(bone_transforms0 - bone_transforms1) < 1e-6))

        delta_transforms2, base_transform2 = anny.models.rigged_model._get_pose_parameterization_with_identity_base_transform(rest_bone_poses, delta_transforms0, base_transform0)
        self.assertTrue(base_transform2 is None)
        bone_poses2, bone_transforms2 = model.get_bone_poses(rest_bone_poses, delta_transforms2, base_transform2)
        self.assertTrue(torch.all(torch.abs(bone_poses0 - bone_poses2) < 1e-6))
        self.assertTrue(torch.all(torch.abs(bone_transforms0 - bone_transforms2) < 1e-6))

        delta_transforms3, base_transform3 = anny.models.rigged_model._get_pose_parameterization_with_translation_only_base_transform(rest_bone_poses, delta_transforms0, base_transform0)
        bone_poses3, bone_transforms3 = model.get_bone_poses(rest_bone_poses, delta_transforms3, base_transform3)
        self.assertTrue(torch.all(torch.abs(delta_transforms3[:,0,:3,3]) < 1e-6))
        self.assertTrue(torch.all(torch.abs(base_transform3[:,:3,:3] - torch.eye(3, dtype=dtype,device=device)[None]) < 1e-6))
        self.assertTrue(torch.all(torch.abs(bone_poses0 - bone_poses3) < 1e-6))
        self.assertTrue(torch.all(torch.abs(bone_transforms0 - bone_transforms3) < 1e-6))