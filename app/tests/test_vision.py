def test_dummy_vision_output():
    detections = [{"class_id": 1, "confidence": 0.87, "bbox": [1, 2, 3, 4]}]
    assert len(detections) == 1
    assert detections[0]["confidence"] > 0.5