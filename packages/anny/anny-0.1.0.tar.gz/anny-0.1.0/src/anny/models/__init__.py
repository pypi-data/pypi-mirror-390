# Anny
# Copyright (C) 2025 NAVER Corp.
# Apache License, Version 2.0
import anny.models.full_model
import torch
from anny.paths import ANNY_CACHE_DIR
from anny.face_segmentation import get_face_segmentation_mask

_eye_bone_labels = {"eye.L", "eye.R"}
_tongue_bone_labels = {"tongue00", "tongue01", "tongue02", "tongue03", "tongue04", "tongue05.L", "tongue05.R",
                       "tongue06.L", "tongue06.R", "tongue07.L", "tongue07.R"}
_facial_expression_bone_labels = {
        "jaw", "special04", "oris02", "oris01", "oris06.L", "oris07.L", "oris06.R", "oris07.R",
        "levator02.L", "levator03.L",
        "levator04.L", "levator05.L", "levator02.R", "levator03.R", "levator04.R", "levator05.R",
        "special01", "oris04.L", "oris03.L", "oris04.R", "oris03.R", "oris06", "oris05", "special03",
        "levator06.L", "levator06.R", "special06.L", "special05.L", "orbicularis03.L",
        "orbicularis04.L", "special06.R", "special05.R", "orbicularis03.R", "orbicularis04.R",
        "temporalis01.L", "oculi02.L", "oculi01.L", "temporalis01.R", "oculi02.R", "oculi01.R",
        "temporalis02.L", "risorius02.L", "risorius03.L", "temporalis02.R", "risorius02.R", "risorius03.R"
}

def create_fullbody_model(rig="default",
                          topology="default",
                          eyes=False,
                          tongue=False,
                          local_changes=False,
                          remove_unattached_vertices=True,
                          triangulate_faces=False,
                          default_pose_parameterization : str = "root_relative_world",
                          extrapolate_phenotypes=False,
                          all_phenotypes=False,
                          cache_dirname=ANNY_CACHE_DIR):
    bones_to_remove = set()
    if not eyes:
        if rig == "default":
            bones_to_remove.update(_eye_bone_labels)
    if not tongue:
        if rig == "default":
            bones_to_remove.update(_tongue_bone_labels)
    return anny.models.full_model.create_model(rig=rig,
                                               topology=topology,
                                                eyes=eyes,
                                                tongue=tongue,
                                                local_changes=local_changes,
                                                bones_to_remove=bones_to_remove,
                                                default_pose_parameterization=default_pose_parameterization,
                                                extrapolate_phenotypes=extrapolate_phenotypes,
                                                all_phenotypes=all_phenotypes,
                                                remove_unattached_vertices=remove_unattached_vertices,
                                                triangulate_faces=triangulate_faces,
                                                cache_dirname=cache_dirname)

def _filter_out_faces(fullbody_model, bones_to_remove):
    bones_to_remove_indices = [i for i, label in enumerate(fullbody_model.bone_labels) if label in bones_to_remove]
    keep_vertices = torch.all(torch.stack([torch.all((fullbody_model.vertex_bone_indices != idx) | (fullbody_model.vertex_bone_weights == 0.), dim=-1) for idx in bones_to_remove_indices], dim=-1), dim=-1)
    faces_to_keep = torch.any(keep_vertices[fullbody_model.faces], dim=-1)
    return faces_to_keep

def create_expressionless_model(rig="default",
                                topology="default",
                                eyes=True,
                                tongue=False,
                                all_phenotypes=False,
                                local_changes=False,
                                remove_unattached_vertices=True,
                                triangulate_faces=False,
                                default_pose_parameterization: str = "root_relative_world",
                                extrapolate_phenotypes=False,
                                cache_dirname=ANNY_CACHE_DIR):
    """"
    ""Create a model with no facial expressions.
    """
    bones_to_remove = set()
    bones_to_remove.update(_facial_expression_bone_labels)
    bones_to_remove.update(_eye_bone_labels)
    bones_to_remove.update(_tongue_bone_labels)
    
    return anny.models.full_model.create_model(rig=rig,
                                               topology=topology,
                                                eyes=eyes,
                                                tongue=tongue,
                                                local_changes=local_changes,
                                                bones_to_remove=bones_to_remove,
                                                remove_unattached_vertices=remove_unattached_vertices,
                                                triangulate_faces=triangulate_faces,
                                                default_pose_parameterization=default_pose_parameterization,
                                                extrapolate_phenotypes=extrapolate_phenotypes,
                                                all_phenotypes=all_phenotypes,
                                                cache_dirname=cache_dirname)

def create_hand_model(side='R',
                      local_changes=False,
                      remove_unattached_vertices=True,
                      triangulate_faces=False,
                      default_pose_parameterization="root_relative",
                      extrapolate_phenotypes=False,
                      all_phenotypes=False,
                      cache_dirname=ANNY_CACHE_DIR):
    hand_bones = {f"wrist.{side}",
                    f"finger1-1.{side}",
                    f"finger1-2.{side}",
                    f"finger1-3.{side}",
                    f"metacarpal1.{side}",
                    f"finger2-1.{side}",
                    f"finger2-2.{side}",
                    f"finger2-3.{side}",
                    f"metacarpal2.{side}",
                    f"finger3-1.{side}",
                    f"finger3-2.{side}",
                    f"finger3-3.{side}",
                    f"metacarpal3.{side}",
                    f"finger4-1.{side}",
                    f"finger4-2.{side}",
                    f"finger4-3.{side}",
                    f"metacarpal4.{side}",
                    f"finger5-1.{side}",
                    f"finger5-2.{side}",
                    f"finger5-3.{side}"}
    
    fullbody_model = anny.models.full_model.create_model(default_pose_parameterization=default_pose_parameterization,
                                                         all_phenotypes=all_phenotypes,
                                                        cache_dirname=cache_dirname)
    bones_to_remove = {label for label in fullbody_model.bone_labels if not label in hand_bones}
    faces_to_keep = get_face_segmentation_mask(fullbody_model, [f"hand.{side}"])

    return anny.models.full_model.create_model(bones_to_remove=bones_to_remove,
                                               faces_to_keep=faces_to_keep,
                                               local_changes=local_changes,
                                               remove_unattached_vertices=remove_unattached_vertices,
                                               triangulate_faces=triangulate_faces,
                                               default_pose_parameterization=default_pose_parameterization,
                                               extrapolate_phenotypes=extrapolate_phenotypes,
                                               all_phenotypes=all_phenotypes,
                                               cache_dirname=cache_dirname)

def create_head_model(eyes=True,
                    tongue=True,
                    local_changes=False,
                    default_pose_parameterization="root_relative",
                    extrapolate_phenotypes=False,
                    all_phenotypes=False,
                    remove_unattached_vertices=True,
                    triangulate_faces=False,
                    cache_dirname=ANNY_CACHE_DIR):
    fullbody_model = anny.models.full_model.create_model(eyes=eyes,
                                                         tongue=tongue,
                                                         default_pose_parameterization=default_pose_parameterization,
                                                         extrapolate_phenotypes=extrapolate_phenotypes,
                                                         all_phenotypes=all_phenotypes,
                                                        cache_dirname=cache_dirname)
    
    face_bones = {"neck01", "neck02", "neck03", "head"}
    face_bones.update(_facial_expression_bone_labels)
    if eyes:
        face_bones.update(_eye_bone_labels)
    if tongue:
        face_bones.update(_tongue_bone_labels)

    bones_to_remove = {label for label in fullbody_model.bone_labels if not label in face_bones}
    faces_to_keep = get_face_segmentation_mask(fullbody_model, ["head",
                                                                "eye_cavity.R",
                                                                "eye_cavity.L",
                                                                "mouth_cavity",
                                                                "eye_front.L",
                                                                "eye_back.L",
                                                                "eye_front.R",
                                                                "eye_back.L",
                                                                "tongue"])

    return anny.models.full_model.create_model(eyes=eyes,
                                               tongue=tongue,
                                               local_changes=local_changes,
                                               bones_to_remove=bones_to_remove,
                                               faces_to_keep=faces_to_keep,
                                               remove_unattached_vertices=remove_unattached_vertices,
                                               triangulate_faces=triangulate_faces,
                                               default_pose_parameterization=default_pose_parameterization,
                                               extrapolate_phenotypes=extrapolate_phenotypes,
                                               all_phenotypes=all_phenotypes,
                                               cache_dirname=cache_dirname)
