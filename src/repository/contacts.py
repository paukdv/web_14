from datetime import datetime, timedelta

from pydantic import EmailStr
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactModel, ResponseContact


async def get_contacts(db: Session):
    """
    The get_contacts function returns a list of all contacts in the database.


    :param db: Session: Pass the database session into the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).all()
    return contacts


async def get_contact(contact_id: int, db):
    """
    The get_contact function returns a contact object from the database.
        Args:
            contact_id (int): The id of the contact to be returned.
            db (object): A connection to the database.

    :param contact_id: int: Specify the contact id of the contact we want to get
    :param db: Query the database for a contact with the given id
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(id=contact_id).first()
    return contact


async def get_contact_by_first_name(first_name: str, db):
    """
    The get_contact_by_first_name function takes in a first_name and returns all contacts with that first name.
        Args:
            first_name (str): The contact's first name.

    :param first_name: str: Filter the contacts by first name
    :param db: Access the database
    :return: A list of response contact objects
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(first_name=first_name).all()
    response_contacts = [ResponseContact(
        id=contact.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        phone_number=contact.phone_number,
        birthday=contact.birthday,
        email=contact.email,
        additional_data=contact.additional_data
    ) for contact in contacts]

    return response_contacts


async def get_contact_by_last_name(last_name: str, db):
    """
    The get_contact_by_last_name function returns a list of contacts with the given last name.

    :param last_name: str: Filter the contacts by last name
    :param db: Pass the database connection to the function
    :return: A list of response contact objects
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(last_name=last_name).all()
    response_contacts = [ResponseContact(
        id=contact.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        phone_number=contact.phone_number,
        birthday=contact.birthday,
        email=contact.email,
        additional_data=contact.additional_data
    ) for contact in contacts]

    return response_contacts


async def get_upcoming_birthdays(db: Session, seven_days_from_now: datetime):
    """
    The get_upcoming_birthdays function returns a list of contacts whose birthdays are within the next seven days.
        Args:
            db (Session): The database session to use for querying.
            seven_days_from_now (datetime): A datetime object representing the date that is exactly 7 days from now.

    :param db: Session: Connect to the database
    :param seven_days_from_now: datetime: Filter the results of the query
    :return: A list of contacts with birthdays in the next 7 days
    :doc-author: Trelent
    """
    upcoming_birthdays = db.query(Contact).filter(Contact.birthday >= datetime.now(),
                                                  Contact.birthday <= seven_days_from_now).all()
    return upcoming_birthdays


async def get_contact_by_email(email: EmailStr, db):
    """
    The get_contact_by_email function returns a contact object from the database
        based on the email address provided.

    :param email: EmailStr: Specify the type of parameter that is expected to be passed into the function
    :param db: Pass the database connection to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(email=email).first()

    return contact


async def create_contact(body: ContactModel, db: Session):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactModel: Define the type of data that is expected to be passed in
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(body: ContactModel, contact_id: int, db: Session):
    """
    The update_contact function updates a contact in the database.
        Args:
            body (ContactModel): The updated contact information.
            contact_id (int): The id of the contact to update.

    :param body: ContactModel: Pass in the json data that is sent to the api
    :param contact_id: int: Identify the contact that is being updated
    :param db: Session: Access the database
    :return: The contact object that was updated
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        contact.additional_data = body.additional_data
        db.commit()
    return contact


async def remove_contact(contact_id: int, db: Session):
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            db (Session): A connection to the database.

    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: Session: Pass the database session to the function
    :return: The contact that was deleted
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact
