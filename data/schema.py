# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
# Modifications Copyright (c) 2025 Armya BAKOUAN -- see NOTICE for details.

import strawberry
from data.image_schema import ImageMutation, ImageQuery, ThinSectionImagePairsQuery, AnnotationMutation


@strawberry.type
class Query(ImageQuery,ThinSectionImagePairsQuery):
    """
    Inherits 'videos' from VideoQuery and 'images' from ImageQuery.
    """
    pass

@strawberry.type
class Mutation(ImageMutation,AnnotationMutation):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
