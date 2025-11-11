# Anny
# Copyright (C) 2025 NAVER Corp.
# Apache License, Version 2.0
import torch
from anny.models.rigged_model import RiggedModelWithLinearBlendShapes
from typing import Union
import anny.utils.interpolation
import anny.utils.relu

def to_batched_tensor(value, device, dtype):
    """
    Helper function to accept float inputs
    """
    value = torch.as_tensor(value, device=device, dtype=dtype)
    if value.dim() == 0:
        return value.unsqueeze(dim=0)
    return value

PHENOTYPE_VARIATIONS = dict(
            race=["african", "asian", "caucasian"],
            gender=["male", "female"],
            age=["newborn", "baby", "child", "young", "old"],
            muscle=["minmuscle", "averagemuscle", "maxmuscle"],
            weight=["minweight", "averageweight", "maxweight"],
            height=["minheight", "maxheight"],
            proportions=["idealproportions", "uncommonproportions"],
            cupsize=["mincup", "averagecup", "maxcup"],
            firmness=["minfirmness", "averagefirmness", "maxfirmness"])

PHENOTYPE_LABELS = [key for key in PHENOTYPE_VARIATIONS.keys() if key != "race"] + PHENOTYPE_VARIATIONS["race"]
EXCLUDED_PHENOTYPES = ['cupsize', 'firmness'] + PHENOTYPE_VARIATIONS["race"]
class BufferDict(torch.nn.Module):
    def __init__(self, input_dict):
        super().__init__()
        for k,v in input_dict.items():
            self.register_buffer(k, v)

    def __getitem__(self, key):
        return getattr(self, key)
class RiggedModelWithPhenotypeParameters(RiggedModelWithLinearBlendShapes):
    """
    A class to deal with a rigged human model with phenotype parameters.
    """
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
                 skinning_method,
                 default_pose_parameterization,
                 stacked_phenotype_blend_shapes_mask,
                 local_change_labels,
                 base_mesh_vertex_indices,
                 extrapolate_phenotypes=False,
                 all_phenotypes=False,
                 ):
        """
        Initialize the RiggedModelWithPhenotypeParameters class.
        Args:
            template_vertices (torch.Tensor): The vertices of the template mesh.
            faces (torch.Tensor): The faces of the mesh.
            blendshapes (torch.Tensor): The blendshapes of the mesh.
            base_mesh_vertex_indices (torch.Tensor): Indices of vertices in the base mesh.
        """
        super().__init__(template_vertices,
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
                 skinning_method=skinning_method,
                 default_pose_parameterization=default_pose_parameterization)
        self.register_buffer("stacked_phenotype_blend_shapes_mask", stacked_phenotype_blend_shapes_mask, persistent=False)
        self.local_change_labels = local_change_labels
        self.base_mesh_vertex_indices = base_mesh_vertex_indices
        self.extrapolate_phenotypes = extrapolate_phenotypes
        self.all_phenotypes = all_phenotypes

        self.phenotype_labels = PHENOTYPE_LABELS if self.all_phenotypes else [x for x in PHENOTYPE_LABELS if x not in EXCLUDED_PHENOTYPES]

        anchors = dict()
        anchors['age'] = torch.linspace(-1/3, 1., len(PHENOTYPE_VARIATIONS["age"]), dtype=template_vertices.dtype, device=template_vertices.device)
        for label in ['gender', 'muscle', 'weight', 'height', 'proportions', 'cupsize', 'firmness']:
            anchors[label] = torch.linspace(0., 1., len(PHENOTYPE_VARIATIONS[label]), dtype=template_vertices.dtype, device=template_vertices.device)
        self.anchors = BufferDict(anchors)
    
    def parse_phenotype_kwargs(self, phenotype_kwargs):
        if type(phenotype_kwargs) is torch.Tensor:
            assert phenotype_kwargs.shape[1] == len(self.phenotype_labels), f"phenotype_kwargs tensor must have shape [bs, {len(self.phenotype_labels)}], got {phenotype_kwargs.shape}"
            phenotype_kwargs = {key: phenotype_kwargs[:,i] for i, key in enumerate(self.phenotype_labels)}
        return phenotype_kwargs
        
    def get_phenotype_blendshape_coefficients(self,
        gender : Union[float, torch.Tensor] = 0.5,
        age : Union[float, torch.Tensor] = 0.5,
        muscle : Union[float, torch.Tensor] = 0.5,
        weight : Union[float, torch.Tensor] = 0.5,
        height : Union[float, torch.Tensor] = 0.5,
        proportions : Union[float, torch.Tensor] = 0.5,
        cupsize : Union[float, torch.Tensor] = 0.5,
        firmness : Union[float, torch.Tensor] = 0.5,
        african : Union[float, torch.Tensor] = 0.5,
        asian : Union[float, torch.Tensor] = 0.5,
        caucasian : Union[float, torch.Tensor] = 0.5,
        local_changes : dict = dict()):
        """
        Return blendshape coefficients corresponding to the input phenotype description.
        """
        stacked_phenotype_blend_shapes_mask = self.stacked_phenotype_blend_shapes_mask
        dtype = stacked_phenotype_blend_shapes_mask.dtype
        device = stacked_phenotype_blend_shapes_mask.device
        
        # Precompute all interpolation weights using vectorized version
        weight_dicts = {}
        batch_size = 1
        for feature, value in zip(
            ['age', 'gender', 'muscle', 'weight', 'height', 'proportions', 'cupsize', 'firmness'],
            [age, gender, muscle, weight, height, proportions, cupsize, firmness]):

            n = len(PHENOTYPE_VARIATIONS[feature])
            
            anchors = self.anchors[feature]
            interpolation_coeffs = anny.utils.interpolation.linear_interpolation_coefficients(to_batched_tensor(value, device, dtype), anchors, extrapolate=self.extrapolate_phenotypes)
            weight_dicts[feature] = {key: interpolation_coeffs[:,i] for i, key in enumerate(PHENOTYPE_VARIATIONS[feature])}
            batch_size = max(batch_size, interpolation_coeffs.shape[0])

        # Race weights, normalized
        race_values = torch.stack([to_batched_tensor(value, device, dtype) for value in (african, asian, caucasian)], dim=1)
        race_weights = torch.nan_to_num(race_values/torch.sum(race_values, dim=1, keepdim=True), 1/3, 1/3, 1/3)

        # Combine all blend shape weights
        dict_phens = {**weight_dicts['age'], **weight_dicts['gender'], **weight_dicts['muscle'],
                    **weight_dicts['weight'], **weight_dicts['height'], **weight_dicts['proportions'],
                    **weight_dicts['cupsize'], **weight_dicts['firmness'], 'african': race_weights[:, 0],
                    'asian': race_weights[:, 1], 'caucasian': race_weights[:, 2]}

        # Stack all the phenotype blend shape weights into one tensor for vectorized processing
        phens = torch.stack([dict_phens[key].expand(batch_size) for key_list in PHENOTYPE_VARIATIONS.values() for key in key_list], dim=1)            

        # Compute blend shapes weights based on phenotype specifications.
        # Step 1: Apply the mask to the phen values
        masked_phens = phens.unsqueeze(1) * stacked_phenotype_blend_shapes_mask.unsqueeze(0)  # shape [bs, 564, num_components]
        # Step 2: Compute the product over the masked phen values along the `num_components` dimension
        wi = torch.prod(masked_phens + (1 - stacked_phenotype_blend_shapes_mask.unsqueeze(0)), dim=-1)  # shape [bs, 564]
        batch_size = len(wi)

        if len(self.local_change_labels) > 0:
            # Consider local changes
            local_weights = torch.zeros((batch_size, 2*len(self.local_change_labels)), device=device, dtype=dtype)
            for i, key in enumerate(self.local_change_labels):
                try:
                    value = to_batched_tensor(local_changes[key], device, dtype)
                    local_weights[:,2*i] = anny.utils.relu.relu_with_gradient_at_zero(value)
                    local_weights[:,2*i+1] = anny.utils.relu.relu_with_gradient_at_zero(-value)
                except KeyError:
                    pass
            wi = torch.cat([wi, local_weights], dim=1)
        return wi
    
    def forward(self,
                pose_parameters=None,
                phenotype_kwargs=dict(),
                local_changes_kwargs=dict(),
                pose_parameterization=None,
                return_bone_ends=False):
        phenotype_kwargs = self.parse_phenotype_kwargs(phenotype_kwargs)
        assert set(phenotype_kwargs) <= set(self.phenotype_labels), f"Invalid phenotype: {set(phenotype_kwargs) - set(self.phenotype_labels)}; available: {self.phenotype_labels}"
        blendshape_coeffs = self.get_phenotype_blendshape_coefficients(**phenotype_kwargs, local_changes=local_changes_kwargs)
        return super().forward(pose_parameters, blendshape_coeffs, pose_parameterization=pose_parameterization, return_bone_ends=return_bone_ends)
        