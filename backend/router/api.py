from fastapi import APIRouter
from router import user, processing_image

router = APIRouter()

# router.include_router(
#     user.router,
#     prefix='/user',
#     tags=['User']
# )

router.include_router(
    processing_image.router,
    prefix='/processing_image',
    tags=['processing_image']
)

# router.include_router(
#     student.router,
#     prefix= '/student',
#     tags=['Student']
# )

