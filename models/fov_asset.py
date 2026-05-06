import uuid

from extensions import db

class FOVAsset(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 1. The Parent: The physical slide seen in image_487bca.jpg
    thin_section_id = db.Column(db.String(50), nullable=False, index=True)

    # 2. The Location: The specific area on the slide
    fov_id = db.Column(db.String(100), nullable=False)

    # 3. The View Type: PPL, XPL, or Reflected
    lighting_modality = db.Column(db.String(10), nullable=False)

    # Gamma logic for compensators:
    # 0 = None (Standard XPL)
    # 1 = Addition (Colors shift up, e.g., GDX-22-PI-XPL-1y-45deg.bmp)
    # -1 = Subtraction (Colors shift down)
    gamma = db.Column(db.Integer, default=0)

    # 5. Rotation: The angle of the microscope stage (0-360)
    stage_angle = db.Column(db.Integer, default=0)

    # Pathing and Metadata
    image_path = db.Column(db.String(255), nullable=False)

    sample_path = db.Column(db.String(255), nullable=False)

    sam_cache_path = db.Column(db.String(255))

    width = db.Column(db.Integer, default=0)

    height = db.Column(db.Integer, default=0)

    thumbnail_path = db.Column(db.String(255), nullable=False)