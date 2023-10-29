from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.connect import get_db
from src.database.models import User, Roles
from src.schemas import ResponseContact, ContactModel
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from src.services.roles import RoleChecker

router = APIRouter(prefix='/contacts', tags=['contacts'])

allowed_get_contacts = RoleChecker([Roles.admin, Roles.moderator, Roles.user])
allowed_create_contacts = RoleChecker([Roles.admin, Roles.moderator, Roles.user])
allowed_update_contacts = RoleChecker([Roles.admin, Roles.moderator])
allowed_remove_contacts = RoleChecker([Roles.admin])


@router.get("/", response_model=List[ResponseContact],
            dependencies=[Depends(allowed_get_contacts), Depends(RateLimiter(times=2, seconds=5))])
async def get_contacts(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts.

    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the current user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(db)
    return contacts


@router.get("/{contact_id}", response_model=ResponseContact, dependencies=[Depends(allowed_get_contacts)])
async def get_contact(contact_id: int = Path(gt=0, ge=1), db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function returns a contact by its ID.

    :param contact_id: int: Get the id of the contact to be updated
    :param ge: Ensure that the contact_id is greater than or equal to 1
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the current user
    :return: A contact object, which is defined in the models
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not found")
    return contact


@router.get("/by_first_name/{first_name}", response_model=List[ResponseContact],
            dependencies=[Depends(allowed_get_contacts)])
async def get_contact_by_first_name(first_name: str, db: Session = Depends(get_db),
                                    current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact_by_first_name function is used to retrieve a contact by first_name.
        The function takes in the first_name of the contact as an argument and returns a JSON object containing all information about that contact.

    :param first_name: str: Specify the first_name of the contact that we want to retrieve
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the auth_service
    :return: The contact with the given first_name
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_first_name(first_name, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="First_name Not found")
    return contact


@router.get("/by_last_name/{last_name}", response_model=List[ResponseContact],
            dependencies=[Depends(allowed_get_contacts)])
async def get_contact_by_last_name(last_name: str, db: Session = Depends(get_db),
                                   current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact_by_last_name function is used to retrieve a contact by last name.
        The function takes in the last_name of the contact as an argument and returns a JSON object containing all information about that contact.

    :param last_name: str: Get the last_name of the contact
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: A single contact by last_name
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_last_name(last_name, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Last_name Not found")
    return contact


@router.get("/by_email/{email}", response_model=ResponseContact, dependencies=[Depends(allowed_get_contacts)])
async def get_contact_by_email(email: str, db: Session = Depends(get_db),
                               current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact_by_email function is used to retrieve a contact by email.
        The function will return the contact if it exists, otherwise it will raise an HTTPException with status code 404 and detail &quot;Email Not found&quot;.


    :param email: str: Get the email of the contact to be deleted
    :param db: Session: Get the database session
    :param current_user: User: Get the user who is currently logged in
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_email(email, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Email Not found")
    return contact


@router.get("/upcoming_birthdays/", response_model=List[ResponseContact], dependencies=[Depends(allowed_get_contacts)])
async def get_upcoming_birthdays(db: Session = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_upcoming_birthdays function returns a list of contacts with birthdays in the next 7 days.

    :param db: Session: Get a database connection from the dependency injection container
    :param current_user: User: Get the current user
    :return: A list of contacts with upcoming birthdays
    :doc-author: Trelent
    """
    seven_days_from_now = datetime.now() + timedelta(days=7)
    upcoming_birthdays = await repository_contacts.get_upcoming_birthdays(db, seven_days_from_now)
    if not upcoming_birthdays:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No upcoming birthdays found")

    return upcoming_birthdays


@router.post("/", response_model=ResponseContact, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_create_contacts)])
async def get_create_contact(body: ContactModel, db: Session = Depends(get_db),
                             current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_create_contact function creates a new contact in the database.
        The function takes in a ContactModel object and returns the newly created contact.

    :param body: ContactModel: Specify the type of data that is expected in the request body
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :return: The contact that was created
    :doc-author: Trelent
    """
    contact = await repository_contacts.create_contact(body, db)
    return contact


@router.put("/{contact_id}", response_model=ResponseContact, dependencies=[Depends(allowed_update_contacts)])
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes an id and a body as input, and returns the updated contact.
        If no such contact exists, it raises an HTTPException with status code 404.

    :param body: ContactModel: Pass the contact information to be updated
    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(body, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not found")

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allowed_remove_contacts)])
async def remove_contact(contact_id: int = Path(gt=0, ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_contact function removes a contact from the database.
        The function takes in an integer representing the id of the contact to be removed,
        and returns a dictionary containing information about that contact.

    :param contact_id: int: Get the id of the contact to be deleted
    :param ge: Check if the contact_id is greater than or equal to 1
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not found")
    return contact
