import os
import sys
import tempfile
import pytest

# Ensure mobile_app directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import LocalDatabase
from localization import get_text

@pytest.fixture
def test_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = LocalDatabase(db_path=path)
    yield db
    if os.path.exists(path):
        os.remove(path)

def test_database_initialization(test_db):
    settings = test_db.get_all_settings()
    assert settings["language"] == "uz"
    assert settings["currency"] == "uzs"

    expense_cats = test_db.get_categories("expense")
    assert len(expense_cats) > 0
    assert any(c["name"] == "Food" for c in expense_cats)

    income_cats = test_db.get_categories("income")
    assert len(income_cats) > 0
    assert any(c["name"] == "Salary" for c in income_cats)

def test_settings_update(test_db):
    test_db.set_setting("language", "en")
    assert test_db.get_setting("language") == "en"

    test_db.set_setting("fullname", "John Doe")
    assert test_db.get_setting("fullname") == "John Doe"

def test_category_management(test_db):
    # Add category
    success = test_db.add_category("expense", "Crypto")
    assert success is True

    # Duplicate category should fail
    duplicate_success = test_db.add_category("expense", "Crypto")
    assert duplicate_success is False

    cats = test_db.get_categories("expense")
    crypto_cat = next((c for c in cats if c["name"] == "Crypto"), None)
    assert crypto_cat is not None

    # Delete category
    del_success = test_db.delete_category(crypto_cat["id"])
    assert del_success is True

    updated_cats = test_db.get_categories("expense")
    assert not any(c["name"] == "Crypto" for c in updated_cats)

def test_add_transaction(test_db):
    trans_id = test_db.add_transaction(
        trans_type="expense",
        amount=50.5,
        currency="usd",
        source="Food",
        additional_info="Lunch"
    )
    assert trans_id is not None and trans_id > 0

    transactions = test_db.get_transactions()
    assert len(transactions) == 1
    t = transactions[0]
    assert t["type"] == "expense"
    assert t["amount"] == 50.5
    assert t["currency"] == "usd"
    assert t["source"] == "Food"
    assert t["additional_info"] == "Lunch"

def test_localization():
    assert get_text("title", "uz") == "Moliya Nazorati"
    assert get_text("title", "en") == "Finance Tracker"
    assert get_text("title", "ru") == "Финансовый Трекер"
