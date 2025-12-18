from energy_app.storage.db import Database
from energy_app.storage.profile_repo import ProfileRepository, Profile


def test_profile_crud(tmp_path):
    db_path = tmp_path / "app.db"
    db = Database(f"sqlite:///{db_path}")
    repo = ProfileRepository(db)
    profile = Profile(user_id="u1", location_text="Budapest", lat=47.5, lon=19.1, area_m2=70, occupants=2)
    repo.upsert_user("u1")
    repo.upsert_profile(profile)
    fetched = repo.get_profile("u1")
    assert fetched is not None
    assert fetched.location_text == "Budapest"
    assert fetched.occupants == 2
