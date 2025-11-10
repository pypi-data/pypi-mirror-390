from enum import Enum

from pydantic import BaseModel


class KeyEnum(str, Enum):
    line_crossed = "line_crossed"
    smart_loiter_detection = "smart_loiter_detection"
    person_idle_time = "person_idle_time"
    vehicle_idle_time = "vehicle_idle_time"
    audio_alarm_speak = "audio_alarm_speak"
    audio_alarm_baby_cry = "audio_alarm_baby_cry"
    audio_alarm_bark = "audio_alarm_bark"
    audio_alarm_co = "audio_alarm_co"
    audio_alarm_smoke = "audio_alarm_smoke"
    audio_alarm_car_horn = "audio_alarm_car_horn"
    audio_alarm_glass_break = "audio_alarm_glass_break"
    audio_alarm_siren = "audio_alarm_siren"
    audio_alarm_burglar = "audio_alarm_burglar"
    smart_tamper_detection = "smart_tamper_detection"
    device_adoption_state_changed = "device_adoption_state_changed"
    device_discovery = "device_discovery"
    admin_access = "admin_access"
    admin_recording_clips_manipulations = "admin_recording_clips_manipulations"
    admin_settings_change = "admin_settings_change"
    device_update_status_change = "device_update_status_change"
    camera_utilization_limit = "camera_utilization_limit"
    application_issue = "application_issue"
    schedule = "schedule"
    face_unknown = "face_unknown"
    face_known = "face_known"
    face_of_interest = "face_of_interest"
    vehicle = "vehicle"
    person = "person"
    animal = "animal"
    license_plate_unknown = "license_plate_unknown"
    license_plate_known = "license_plate_known"
    license_plate_of_interest = "license_plate_of_interest"
    include = "include"
    motion = "motion"


class UnifiAlarmSource(BaseModel):
    type: KeyEnum
    device: str
