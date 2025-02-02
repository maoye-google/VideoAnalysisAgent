class DetectedObject:
    def __init__(self, frame_id, object_type, object_color, object_description=None):
        self.frame_id = frame_id
        self.object_type = object_type
        self.object_color = object_color
        self.object_description = object_description