import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.schemas import ContactModel, ResponseContact
from src.database.models import Contact
from src.repository.contacts import (
    get_contacts,
    get_contact,
    get_contact_by_first_name,
    get_contact_by_last_name,
    get_upcoming_birthdays,
    get_contact_by_email,
    create_contact,
    update_contact,
    remove_contact,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.contact = Contact(id=1, first_name='Dmytro', last_name='Test', email='paukdv_test@gmail.com',
                               phone_number='0677772332', birthday='1990-01-11', additional_data='Additional 1')

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().all.return_value = contacts
        result = await get_contacts(self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = [Contact(), Contact(), Contact()]
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact(contact_id=self.contact.id, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await get_contact(contact_id=self.contact.id, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(
            id=2,
            first_name='Stefan',
            last_name='Stefanos',
            phone_number='0989876655',
            birthday='1961-10-23',
            email='stefan@meta.com.ua',
            additional_data='Empty',
        )
        result = await create_contact(body=body, db=self.session)
        self.assertEqual(result.id, body.id)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.additional_data, body.additional_data)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact_found(self):
        body = ContactModel(
            id=2,
            first_name='Stefanka',
            last_name='Stefanos',
            phone_number='0989876655',
            birthday='1961-10-23',
            email='stefan@meta.com.ua',
            additional_data='Empty',
        )
        contact = Contact(
            id=2,
            first_name='Stefania',
            last_name='Stefano',
            phone_number='0989876655',
            birthday='1961-10-23',
            email='stefan@meta.com.ua',
            additional_data='Empty',
        )
        self.session.query().filter_by().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(body=body, contact_id=self.contact.id, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactModel(
            id=2,
            first_name='Stefanka',
            last_name='Stefanos',
            phone_number='0989876655',
            birthday='1961-10-23',
            email='stefan@meta.com.ua',
            additional_data='Empty',
        )
        contact = Contact(
            id=2,
            first_name='Stefania',
            last_name='Stefano',
            phone_number='0989876655',
            birthday='1961-10-23',
            email='stefan@meta.com.ua',
            additional_data='Empty',
        )
        self.session.query().filter_by().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(body=body, contact_id=self.contact.id, db=self.session)
        self.assertIsNone(result)

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await remove_contact(contact_id=1, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await remove_contact(contact_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_contact_by_first_name_found(self):
        self.session.query().filter_by().all.return_value = [self.contact]
        result = await get_contact_by_first_name(first_name=self.contact.first_name, db=self.session)

        expected_result = [ResponseContact(
            id=self.contact.id,
            first_name=self.contact.first_name,
            last_name=self.contact.last_name,
            email=self.contact.email,
            phone_number=self.contact.phone_number,
            birthday=self.contact.birthday,
            additional_data=self.contact.additional_data
        )]
        self.assertEqual(result, expected_result)

    async def test_contact_by_first_name_not_found(self):
        self.session.query().filter_by().all.return_value = []
        result = await get_contact_by_first_name(first_name=self.contact.first_name, db=self.session)
        self.assertEqual(result, [])

    async def test_contact_by_last_name_found(self):
        self.session.query().filter_by().all.return_value = [self.contact]
        result = await get_contact_by_last_name(last_name=self.contact.last_name, db=self.session)

        expected_result = [ResponseContact(
            id=self.contact.id,
            first_name=self.contact.first_name,
            last_name=self.contact.last_name,
            email=self.contact.email,
            phone_number=self.contact.phone_number,
            birthday=self.contact.birthday,
            additional_data=self.contact.additional_data
        )]
        self.assertEqual(result, expected_result)

    async def test_contact_by_last_name_not_found(self):
        self.session.query().filter_by().all.return_value = []
        result = await get_contact_by_last_name(last_name=self.contact.last_name, db=self.session)
        self.assertEqual(result, [])

    async def test_contact_by_email_found(self):
        self.session.query().filter_by().first.return_value = self.contact
        result = await get_contact_by_email(email=self.contact.email, db=self.session)

        self.assertEqual(result, self.contact)

    async def test_contact_by_email_not_found(self):
        self.session.query().filter_by().first.return_value = []
        result = await get_contact_by_email(email=self.contact.email, db=self.session)
        self.assertEqual(result, [])

    async def test_get_upcoming_birthdays_found(self):
        self.session.query().filter().all.return_value = self.contact
        result = await get_upcoming_birthdays(seven_days_from_now=self.contact.birthday, db=self.session)

        self.assertEqual(result, self.contact)

    async def test_get_upcoming_birthdays_not_found(self):
        self.session.query().filter().all.return_value = None
        result = await get_upcoming_birthdays(seven_days_from_now=self.contact.birthday, db=self.session)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
