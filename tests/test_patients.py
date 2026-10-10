from database.models import Patientsql, Doctors
from unittest.mock import patch
from uploads.uploads import UPLOAD_DIR
from uploads import uploads
import pytest




def test_doctor_can_read(client_for_role):
    client = client_for_role("doctor")

    response = client.get("/api/v1/patients")

    assert response.status_code == 200


def test_doctor_can_create(client_for_role):
    client = client_for_role("doctor")

    response = client.post(
        "/api/v1/patients",
        json={
            "name": "Doctor Patient",
            "age": 30,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert response.status_code == 201


def test_doctor_can_update(client_for_role):
    client = client_for_role("doctor")

    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Ali",
            "age": 25,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert create_response.status_code == 201

    patient_id = create_response.json()["data"]["id"]

    response = client.put(
        f"/api/v1/patients/{patient_id}",
        json={
            "name": "Ali Updated",
            "age": 26,
            "disease": "Cold",
            "city": "Tehran"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["name"] == "Ali Updated"
    assert data["data"]["age"] == 26
    assert data["data"]["disease"] == "Cold"


def test_doctor_cannot_delete(client_for_role):
    client = client_for_role("doctor")

    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Ali",
            "age": 25,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert create_response.status_code == 201

    patient_id = create_response.json()["data"]["id"]

    response = client.delete(
        f"/api/v1/patients/{patient_id}"
    )

    assert response.status_code == 403


def test_nurse_can_read(client_for_role):
    client = client_for_role("nurse")

    response = client.get("/api/v1/patients")

    assert response.status_code == 200


def test_nurse_cannot_create(client_for_role):
    client = client_for_role("nurse")

    response = client.post(
        "/api/v1/patients",
        json={
            "name": "Nurse Patient",
            "age": 30,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert response.status_code == 403


def test_nurse_cannot_update(client_for_role):
    client = client_for_role("nurse")

    response = client.put(
        "/api/v1/patients/1",
        json={
            "name": "Ali Updated",
            "age": 26,
            "disease": "Cold",
            "city": "Tehran"
        }
    )

    assert response.status_code == 403


def test_nurse_cannot_delete(client_for_role):
    client = client_for_role("nurse")

    response = client.delete("/api/v1/patients/1")

    assert response.status_code == 403


def test_admin_can_read(client_for_role):
    client = client_for_role("admin")

    response = client.get("/api/v1/patients")

    assert response.status_code == 200


def test_admin_can_create(client_for_role):
    client = client_for_role("admin")

    response = client.post(
        "/api/v1/patients",
        json={
            "name": "Admin Patient",
            "age": 40,
            "disease": "Diabetes",
            "city": "Tehran"
        }
    )

    assert response.status_code == 201


def test_admin_can_delete(client_for_role):
    client = client_for_role("admin")

    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Delete Patient",
            "age": 35,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert create_response.status_code == 201

    patient_id = create_response.json()["data"]["id"]

    response = client.delete(
        f"/api/v1/patients/{patient_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"] is None


def test_create_patient(client, db):
    response = client.post(
        "/api/v1/patients",
        json={
            "name": "Test Patient",
            "age": 30,
            "disease": "Diabetes",
            "city": "Shiraz"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["success"] is True
    assert data["data"]["name"] == "Test Patient"
    assert data["data"]["age"] == 30
    assert data["data"]["disease"] == "Diabetes"
    assert data["data"]["city"] == "Shiraz"

    patient_id = data["data"]["id"]

    patient = db.get(Patientsql, patient_id)

    assert patient is not None
    assert patient.name == "Test Patient"
    assert patient.age == 30
    assert patient.disease == "Diabetes"
    assert patient.city == "Shiraz"




def test_update_patient(client):
    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Ali",
            "age": 25,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert create_response.status_code == 201

    patient_id = create_response.json()["data"]["id"]

    response = client.put(
        f"/api/v1/patients/{patient_id}",
        json={
            "name": "Ali Updated",
            "age": 30,
            "disease": "Cold",
            "city": "Shiraz"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["name"] == "Ali Updated"
    assert data["data"]["age"] == 30
    assert data["data"]["disease"] == "Cold"
    assert data["data"]["city"] == "Shiraz"


def test_update_nonexistent_patient(client):
    response = client.put(
        "/api/v1/patients/99999",
        json={
            "name": "Nobody",
            "age": 30,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert response.status_code == 404




def test_patch_patient(client):
    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Sara",
            "age": 25,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert create_response.status_code == 201

    patient_id = create_response.json()["data"]["id"]

    response = client.patch(
        f"/api/v1/patients/{patient_id}",
        json={
            "age": 30
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["age"] == 30


def test_patch_multiple_fields(client):
    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Sara",
            "age": 25,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    patient_id = create_response.json()["data"]["id"]

    response = client.patch(
        f"/api/v1/patients/{patient_id}",
        json={
            "name": "Sara Updated",
            "disease": "Cold",
            "city": "Shiraz"
        }
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["name"] == "Sara Updated"
    assert data["age"] == 25
    assert data["disease"] == "Cold"
    assert data["city"] == "Shiraz"


def test_patch_nonexistent_patient(client):
    response = client.patch(
        "/api/v1/patients/99999",
        json={
            "age": 40
        }
    )

    assert response.status_code == 404


def test_delete_patient(client):
    response = client.post(
        "/api/v1/patients",
        json={
            "name": "Ali",
            "age": 30,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert response.status_code == 201

    patient_id = response.json()["data"]["id"]

    response = client.delete(
        f"/api/v1/patients/{patient_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"] is None


def test_delete_nonexistent_patient(client):
    response = client.delete(
        "/api/v1/patients/99999"
    )

    assert response.status_code == 404


def test_filter_search_sort_pagination(client):
    patients = [
        {
            "name": "Ali",
            "age": 25,
            "disease": "Flu",
            "city": "Tehran"
        },
        {
            "name": "Ali Reza",
            "age": 35,
            "disease": "Flu",
            "city": "Shiraz"
        },
        {
            "name": "Sara",
            "age": 40,
            "disease": "Cold",
            "city": "Bandar"
        },
        {
            "name": "Maryam",
            "age": 45,
            "disease": "Flu",
            "city": "Tabriz"
        },
        {
            "name": "Reza",
            "age": 60,
            "disease": "Diabetes",
            "city": "Ardabil"
        }
    ]

    for patient in patients:
        response = client.post(
            "/api/v1/patients",
            json=patient
        )

        assert response.status_code == 201

    response = client.get(
        "/api/v1/patients"
        "?page=1"
        "&limit=2"
        "&disease=Flu"
        "&city=Tehran"
        "&search=Ali"
        "&sort=age"
        "&order=desc"
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert data["total_pages"] == 1
    assert data["has_next"] is False
    assert data["has_previous"] is False

    assert data["items"][0]["name"] == "Ali Reza"
    assert data["items"][0]["age"] == 35

    assert data["items"][1]["name"] == "Ali"
    assert data["items"][1]["age"] == 25


def test_upload_file(client):
    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Upload Patient",
            "age": 30,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert create_response.status_code == 201

    patient_id = create_response.json()["data"]["id"]

    response = client.post(
        f"/api/v1/files/upload/{patient_id}",
        files={
            "file": (
                "test.pdf",
                b"%PDF-1.4 test pdf",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "File uploaded successfully"
    assert data["patient_id"] == patient_id
    assert "filename" in data


def test_upload_file_for_nonexistent_patient(client):
    response = client.post(
        "/api/v1/files/upload/99999",
        files={
            "file": (
                "test.pdf",
                b"%PDF-1.4 test pdf",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 404



def test_get_patient_files(client):
    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "File Patient",
            "age": 30,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    patient_id = create_response.json()["data"]["id"]

    upload_response = client.post(
        f"/api/v1/files/upload/{patient_id}",
        files={
            "file": (
                "test.pdf",
                b"%PDF-1.4 test pdf",
                "application/pdf"
            )
        }
    )

    assert upload_response.status_code == 200

    response = client.get(
        f"/api/v1/patients/{patient_id}/files"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["patient_id"] == patient_id
    assert len(data["files"]) == 1


def test_get_files_for_nonexistent_patient(client):
    response = client.get(
        "/api/v1/patients/99999/files"
    )

    assert response.status_code == 404




def test_download_patient_file(client):
    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Download Patient",
            "age": 30,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    patient_id = create_response.json()["data"]["id"]

    upload_response = client.post(
        f"/api/v1/files/upload/{patient_id}",
        files={
            "file": (
                "test.pdf",
                b"%PDF-1.4 test pdf",
                "application/pdf"
            )
        }
    )

    assert upload_response.status_code == 200

    filename = upload_response.json()["filename"]

    response = client.get(
        f"/api/v1/patients/{patient_id}/files/{filename}"
    )

    assert response.status_code == 200



def test_stream_patient_file(client):
    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Stream Patient",
            "age": 30,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    patient_id = create_response.json()["data"]["id"]

    upload_response = client.post(
        f"/api/v1/files/upload/{patient_id}",
        files={
            "file": (
                "test.pdf",
                b"%PDF-1.4 test pdf",
                "application/pdf"
            )
        }
    )

    assert upload_response.status_code == 200

    filename = upload_response.json()["filename"]

    response = client.get(
        f"/api/v1/patients/{patient_id}/files/{filename}/stream"
    )

    assert response.status_code == 200
    assert response.content == b"%PDF-1.4 test pdf"



def test_delete_patient_file(client):
    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Delete File Patient",
            "age": 30,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    patient_id = create_response.json()["data"]["id"]

    upload_response = client.post(
        f"/api/v1/files/upload/{patient_id}",
        files={
            "file": (
                "test.pdf",
                b"%PDF-1.4 test pdf",
                "application/pdf"
            )
        }
    )

    assert upload_response.status_code == 200

    filename = upload_response.json()["filename"]

    response = client.delete(
        f"/api/v1/patients/{patient_id}/files/{filename}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "File deleted successfully"
    assert data["filename"] == filename
    assert data["patient_id"] == patient_id




def test_assign_doctor_to_patient(client, db):
    patient = Patientsql(
        name="Patient One",
        age=30,
        disease="Flu",
        city="Tehran"
    )

    doctor = Doctors(
        name="Dr. Ali",
        specialty="Cardiology"
    )

    db.add(patient)
    db.add(doctor)
    db.commit()

    db.refresh(patient)
    db.refresh(doctor)

    response = client.post(
        f"/api/v1/patients/{patient.id}/doctors/{doctor.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["patient_id"] == patient.id
    assert data["doctor_id"] == doctor.id


def test_assign_nonexistent_doctor(client, db):
    patient = Patientsql(
        name="Patient One",
        age=30,
        disease="Flu",
        city="Tehran"
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    response = client.post(
        f"/api/v1/patients/{patient.id}/doctors/99999"
    )

    assert response.status_code == 404


def test_assign_doctor_to_nonexistent_patient(client, db):
    doctor = Doctors(
        name="Dr. Ali",
        specialty="Cardiology"
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    response = client.post(
        f"/api/v1/patients/99999/doctors/{doctor.id}"
    )

    assert response.status_code == 404



def test_upload_file_with_invalid_type(client):
    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Invalid File Patient",
            "age": 30,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert create_response.status_code == 201
    patient_id = create_response.json()["data"]["id"]

    response = client.post(
        f"/api/v1/files/upload/{patient_id}",
        files={
            "file": (
                "test.exe",
                b"fake executable content",
                "application/octet-stream"
            )
        }
    )

    assert response.status_code in (400, 415, 422)


def test_upload_file_too_large(client):
    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Large File Patient",
            "age": 30,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert create_response.status_code == 201
    patient_id = create_response.json()["data"]["id"]

    response = client.post(
        f"/api/v1/files/upload/{patient_id}",
        files={
            "file": (
                "large.pdf",
                b"x" * (10 * 1024 * 1024 + 1),
                "application/pdf"
            )
        }
    )

    assert response.status_code in (400, 413, 422)


def test_get_doctor_patients(client, db):
    patient = Patientsql(
        name="Patient One",
        age=30,
        disease="Flu",
        city="Tehran"
    )

    doctor = Doctors(
        name="Dr. Ali",
        specialty="Cardiology"
    )

    doctor.patients.append(patient)

    db.add(doctor)
    db.commit()

    db.refresh(doctor)

    response = client.get(
        f"/api/v1/doctors/{doctor.id}/patients"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == patient.id
    assert data[0]["name"] == "Patient One"


def test_get_patients_for_nonexistent_doctor(client):
    response = client.get(
        "/api/v1/doctors/99999/patients"
    )

    assert response.status_code == 404




def test_delete_doctor_without_patients(client, db):
    doctor = Doctors(
        name="Dr. Delete",
        specialty="Neurology"
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    response = client.delete(
        f"/api/v1/doctors/{doctor.id}"
    )

    assert response.status_code == 200


def test_cannot_delete_doctor_with_patients(client, db):
    patient = Patientsql(
        name="Patient One",
        age=30,
        disease="Flu",
        city="Tehran"
    )

    doctor = Doctors(
        name="Dr. Busy",
        specialty="Cardiology"
    )

    doctor.patients.append(patient)

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    response = client.delete(
        f"/api/v1/doctors/{doctor.id}"
    )

    assert response.status_code == 400

def test_upload_file_db_failure_removes_saved_file(
    client, db, tmp_path, monkeypatch
):
    monkeypatch.setattr(uploads, "UPLOAD_DIR", tmp_path)

    create_response = client.post(
        "/api/v1/patients",
        json={
            "name": "Rollback Patient",
            "age": 30,
            "disease": "Flu",
            "city": "Tehran"
        }
    )

    assert create_response.status_code == 201
    patient_id = create_response.json()["data"]["id"]

    with patch.object(
        db, "commit", side_effect=Exception("DB error")
    ):
        response = client.post(
            f"/api/v1/files/upload/{patient_id}",
            files={
                "file": (
                    "rollback_test.pdf",
                    b"%PDF-1.4 test pdf",
                    "application/pdf"
                )
            }
        )

    assert response.status_code == 500
    assert list(tmp_path.iterdir()) == []