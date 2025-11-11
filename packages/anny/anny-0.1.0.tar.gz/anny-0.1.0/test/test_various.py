import unittest
import torch
import anny
import roma

class TestVarious(unittest.TestCase):
    def test_batch_consistency(self):
        batch_size = 32
        dtype = torch.float64
        device = torch.device('cpu')
        model = anny.create_fullbody_model().to(dtype=dtype, device=device)
        torch.use_deterministic_algorithms(True)

        def apply_model(phenotype_kwargs, delta_transforms):
            blendshape_coeffs = model.get_phenotype_blendshape_coefficients(**phenotype_kwargs)
            rest_vertices = model.get_rest_vertices(blendshape_coeffs)
            rest_bone_heads, rest_bone_tails, rest_bone_poses = model.get_rest_bone_poses(blendshape_coeffs)
            bone_poses, bone_transforms = model.get_bone_poses(rest_bone_poses, delta_transforms)
            vertices = model.get_skinned_vertices(rest_vertices, bone_transforms)
            return dict(blendshape_coeffs=blendshape_coeffs,
                        rest_vertices=rest_vertices,
                        rest_bone_heads=rest_bone_heads,
                        rest_bone_tails=rest_bone_tails,
                        rest_bone_poses=rest_bone_poses,
                        bone_poses=bone_poses,
                        bone_transforms=bone_transforms,
                        vertices=vertices)


        joints_relative_transforms = {}
        for k in model.bone_labels:
            rot = roma.random_rotmat(batch_size, dtype=dtype, device=device)
            joints_relative_transforms[k] = roma.Rigid(rot, torch.zeros((batch_size,3), dtype=dtype, device=device)).to_homogeneous()      
        delta_transforms = model.parse_delta_transforms_dict(joints_relative_transforms)

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

        epsilon = 1e-8
        for skinning_method in ['lbs', 'dqs', 'warp_lbs']:
            model.set_skinning_method(skinning_method)

            # Run the model
            batched_results = apply_model(phenotype_kwargs, delta_transforms)

            # Ensure batch consistency by performing computations for a single element
            for i in range(batch_size):
                results = apply_model({key : value[None,i] for key, value in phenotype_kwargs.items()}, delta_transforms[None,i])
                for key in batched_results.keys():
                    self.assertTrue(torch.all(torch.abs(batched_results[key][i] - results[key].squeeze(dim=0)) < epsilon))

    def test_local_changes(self):
        """
        Ensure that default local changes params have no impact on 
        """
        batch_size = 32
        dtype = torch.float64
        device = torch.device('cpu')
        model = anny.create_fullbody_model().to(dtype=dtype, device=device)
        model_local_changes = anny.create_fullbody_model(local_changes=True).to(dtype=dtype, device=device)
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
        
        blendshape_coeffs0 = model.get_phenotype_blendshape_coefficients(**phenotype_kwargs)
        rest_vertices0 = model.get_rest_vertices(blendshape_coeffs0)
        rest_bone_heads0, rest_bone_tails0, rest_bone_poses0 = model.get_rest_bone_poses(blendshape_coeffs0)

        blendshape_coeffs1 = model_local_changes.get_phenotype_blendshape_coefficients(**phenotype_kwargs)
        rest_vertices1 = model_local_changes.get_rest_vertices(blendshape_coeffs1)
        rest_bone_heads1, rest_bone_tails1, rest_bone_poses1 = model_local_changes.get_rest_bone_poses(blendshape_coeffs1)

        blendshape_coeffs2 = model_local_changes.get_phenotype_blendshape_coefficients(**phenotype_kwargs, local_changes={key: torch.zeros((batch_size,), dtype=dtype, device=device) for key in model_local_changes.local_change_labels})
        rest_vertices2 = model_local_changes.get_rest_vertices(blendshape_coeffs2)
        rest_bone_heads2, rest_bone_tails2, rest_bone_poses2 = model_local_changes.get_rest_bone_poses(blendshape_coeffs2)

        self.assertTrue(torch.all(torch.abs(rest_vertices1 - rest_vertices0) < 1e-3))
        self.assertTrue(torch.all(torch.abs(rest_vertices2 - rest_vertices0) < 1e-3))

        self.assertTrue(torch.all(torch.abs(rest_bone_heads1 - rest_bone_heads0) < 1e-3))
        self.assertTrue(torch.all(torch.abs(rest_bone_heads2 - rest_bone_heads0) < 1e-3))

        self.assertTrue(torch.all(torch.abs(rest_bone_tails1 - rest_bone_tails0) < 1e-3))
        self.assertTrue(torch.all(torch.abs(rest_bone_tails1 - rest_bone_tails0) < 1e-3))

        self.assertTrue(torch.all(torch.abs(rest_bone_poses1 - rest_bone_poses0) < 1e-3))
        self.assertTrue(torch.all(torch.abs(rest_bone_poses2 - rest_bone_poses0) < 1e-3))