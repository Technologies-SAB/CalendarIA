from sqlalchemy.orm import Session
import models, security
import json

def get_user_by_chat_id(db: Session, chat_id: str) -> models.User | None:
    return db.query(models.User).filter(models.User.chat_id == chat_id).first()

def create_user(db: Session, chat_id: str) -> models.User:
    db_user = models.User(chat_id=chat_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_accounts(db: Session, user: models.User) -> list[models.Account]:
    return db.query(models.Account).filter_by(owner=user).all()

def create_or_update_account(db: Session, user: models.User, provider: str, credentials: dict) -> models.Account:
    account = db.query(models.Account).filter_by(owner=user, provider_name=provider).first()
    
    credentials_json = json.dumps(credentials)
    encrypted_creds = security.encrypt_data(credentials_json)

    if account:
        account.encrypted_credentials = encrypted_creds
    else:
        account = models.Account(
            provider_name=provider.lower(),
            encrypted_credentials=encrypted_creds,
            owner=user
        )
        db.add(account)
    
    db.commit()
    db.refresh(account)
    
    return account

def update_account_credentials(db: Session, account: models.Account, new_credentials: dict):
    credentials_json = json.dumps(new_credentials)
    encrypted_creds = security.encrypt_data(credentials_json)
    account.encrypted_credentials = encrypted_creds
    db.commit()
    db.refresh(account)
    return account