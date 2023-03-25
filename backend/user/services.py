from backend import db
from backend.user.models import User
from backend.user_type.models import UserType
from backend.user.schemas import user_schema
from sqlalchemy import and_
import re

def create_user(data):
    """Given serialized data and create a ner User"""
    if not len(data['body'].get('id')) >= 4 and len(data['body'].get('id')) <= 10:
        return 'please id rule check', 505
    '''
    if not len(data['body'].get('pw')) >= 5 and len(data['body'].get('pw')) <= 15:
        return 'Check the password length', 505

    if not re.findall('[0-9]+', data['body'].get('pw')) and not re.findall('[a-z]', data['body'].get('pw')) or not re.findall(
            '[A-Z]', data['body'].get('pw')):
        return 'please password rule check', 505

    if not re.findall('[`~!@#$%^&*(),<.>/?]+', data['body'].get('pw')):
        return 'At least 1 special character required', 505

    if not data['body'].get('pw') == data['body'].get('pw_chk'):
        return 'password and chk_pwd do not match', 505
    '''
    user = User(id=data['body'].get('id'), password=data['body'].get('pw'),
                name=data['body'].get('name'), email=data['body'].get('email'), uno=1)
    db.session.add(user)
    db.session.commit()
    return user_schema.dump(user), 201

def login_user(data):
    """Login User"""
    res = db.session.query(User).filter(and_(User.id == data['body'].get('id'), User.password == data['body'].get('pw'))).all()
    if not res :
        return 'fail', 505
    result = {
        'uno': res[0].uno
    }

    return result, 200

def delete_user(data):
    """Delete User"""
    res = db.session.query(User).filter(and_(User.id == data['body'].get('id'), User.password == data['body'].get('pw'))).all()

    if not res:
        return 'fail', 505

    for r in res:
        db.session.delete(r)
        db.session.commit()

    return 'Delete OK', 200

def update_user(data):
    """Update User"""
    res = db.session.query(User).filter(User.id == data['body'].get('id')).update(
        {"email": data['body'].get('email'), "name": data['body'].get('name')})

    if not res:
        return 'fail', 505

    pw = db.session.query(User).filter(User.password == data['body'].get('pw')).all()

    if not pw :
        return 'pwd fail', 505

    db.session.commit()

    return 'Update OK', 200

def pwupdate_user(data):
    """Pwupdate User"""
    res = db.session.query(User).filter(and_(User.id == data['body'].get('id'), User.password == data['body'].get('pw'),
                                             data['body'].get('newpw') == data['body'].get('newpw_chk'))).update({"password": data['body'].get('newpw')}, synchronize_session=False)

    if not len(data['body'].get('newpw')) >= 5 and len(data['body'].get('newpw')) <= 15:
        return 'Check the password length', 505

    if not re.findall('[0-9]+', data['body'].get('newpw')) and not re.findall('[a-z]', data['body'].get('newpw')) or not re.findall('[A-Z]', data['body'].get('newpw')) :
        return 'please password rule check', 505

    if not re.findall('[`~!@#$%^&*(),<.>/?]+', data['body'].get('newpw')):
        return 'At least 1 special character required', 505

    if not data['body'].get('newpw') == data['body'].get('newpw_chk') :
        return 'new_pwd and new_pwd_chk do not match', 505

    if not res:
        return 'fail', 505

    db.session.commit()

    return 'Pwupdate OK', 200

def search_id(data):
    """search id"""
    res = db.session.query(User).filter(and_(User.name == data['body'].get('name'), User.email == data['body'].get('email'))).first()
    if not res:
        return 'fail', 505

    result= {
        'id': res.id
    }
    return result, 200

def search_pw(data):
    """search pw"""
    res = db.session.query(User).filter(and_(User.id == data['body'].get('id'), User.name == data['body'].get('name'), User.email == data['body'].get('email'))).first()

    if not res:
        return 'fail', 505

    result= {
        'pw': res.password
    }
    return result, 200

def check_overlap_id(data):
    """Check Overlap Id"""
    res = db.session.query(User).filter(User.id == data['body'].get('id')).all()

    if not res:
        return 'OK', 200

    return 'fail', 505

def check_overlap_email(data):
    """Check Overlap Email"""
    res = db.session.query(User).filter(User.email == data['body'].get('email')).all()

    if not res :
        return 'OK', 200

    return 'fail', 505

def read_user(data):
    """Read User"""
    user = db.session.query(User).filter(User.id == data['body'].get('id')).all()
    if not user:
        return 'fail', 505

    result = {}

    for data in user:
        temp = data.__dict__
        del temp['_sa_instance_state']
        del temp['password']
        del temp['uno']
        result['user'] = temp

    print(result)
    return {'result':result}, 200


def read_all_users(data):
    """Read All Users"""
    user_type = db.session.query(UserType).filter(UserType.uno == data['body'].get('uno')).first()
    if user_type is None or user_type.type != 'admin':
        return {"message": f"only admin can read"}, 505

    res = db.session.query(User).filter(User.uno == 1).all()

    if not res:
        return 'fail', 505

    result = {}

    for data in res:
        temp = data.__dict__
        del temp['_sa_instance_state']
        del temp['password']
        result[temp.get('id')] = temp

    return result, 200

def delete_user_admin(data):
    """Delete User Admin"""
    user_type = db.session.query(UserType).filter(UserType.uno == data['body'].get('uno')).first()
    if user_type is None or user_type.type != 'admin':
        return {"message": f"only admin can delete"}, 505

    res = db.session.query(User).filter(User.id == data['body'].get('id')).all()

    if not res:
        return 'fail', 505

    for r in res:
        db.session.delete(r)
        db.session.commit()

    return 'Delete OK', 200

def search_user(data):
    """Search user"""
    id_result = db.session.query(User).with_entities(User.id, User.name).filter(User.id.like('%' + data['searchData'] + '%')).all()
    name_result = db.session.query(User).with_entities(User.id, User.name).filter(User.name.like('%' + data['searchData'] + '%')).all()


    if not id_result:
        id_result = ""

    if not name_result:
        name_result = ""


    result = {}

    if id_result != "":
        i = 0
        for data in id_result:
            temp = {}
            temp['id'] = data[0]
            temp['name'] = data[1]
            temp['email'] = data[2]
            result['id_result' + str(i)] = temp
            i+=1

    if name_result != "":
        i = 0
        for data in name_result:
            temp = {}
            temp['id'] = data[0]
            temp['name'] = data[1]
            temp['email'] = data[2]
            result['name_result' + str(i)] = temp
            i += 1

    return result, 200