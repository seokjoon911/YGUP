from backend import db
from backend.company.models import Company
from backend.bookmark.models import Bookmark
from backend.company.schemas import company_schema
import uuid
from backend.user_type.models import UserType
from sqlalchemy import desc, func
from werkzeug.utils import secure_filename
from flask import request
def create_company(data):
    """Given serialized data and create a ner Company"""
    usertype = db.session.query(UserType).filter(UserType.type == data['body'].get('data').get('uno')).first()
    if usertype is None or usertype.type != 'admin':
        return {"message": f"only admin can create"}, 505
    cno = {'cno': str(uuid.uuid1())}
    data['body'].get('data').update(cno)
    keyword = {'keyword': str(uuid.uuid1())}
    data['body'].get('data').update(keyword)
    #북마크 테이블이 완성 되면 북마크 조회해서 값 채워 넣기
    company = Company(cname=data['body'].get('data').get('cname'), cno=data['body'].get('data').get('cno'),
    keyword=data['body'].get('data').get('keyword'), address=data['body'].get('data').get('address'),
    sales=data['body'].get('data').get('sales'), owner=data['body'].get('data').get('owner'),
    info=data['body'].get('data').get('cname'),pay=data['body'].get('data').get('pay'),
    courl=data['body'].get('data').get('courl'),
    resign=data['body'].get('data').get('resign'), form=data['body'].get('data').get('form'), bookmarkcnt=0,
    readcnt=0)
    db.session.add(company)
    db.session.commit()
    return company_schema.dump(company), 201

def update_company(data):
    """Update company"""
    usertype = db.session.query(UserType).filter(UserType.type == data['body'].get('data').get('uno')).first()
    if usertype is None or usertype.type != 'admin':
       return {"message": f"only admin can update"}, 505

    res = db.session.query(Company).filter(Company.cname == data['body'].get('data').get('cname')).update(
        {"cname": data['body'].get('data').get('cname'),
          "address": data['body'].get('data').get('address'),
         "sales": data['body'].get('data').get('sales'), "owner": data['body'].get('data').get('owner'),
         "info": data['body'].get('data').get('info'), "pay": data['body'].get('data').get('pay'),
         "courl": data['body'].get('data').get('courl'),
         "resign": data['body'].get('data').get('resign'), "form": data['body'].get('data').get('form') })

    if not res:
        return 'fail', 505

    db.session.commit()

    return 'Update OK', 200

def delete_company(data):
    """Delete Company"""
    user_type = db.session.query(UserType).filter(UserType.uno == data['body'].get('uno')).first()
    if user_type is None or user_type.type != 'admin':
        return {"message": f"only admin can delete"}, 505

    res = db.session.query(Company).filter(Company.cname == data['body'].get('cname')).all()

    if not res:
        return 'fail', 503

    for r in res:
        db.session.delete(r)
        db.session.commit()

def read_all_company(data):
    """Read All Company"""
    usertype = db.session.query(UserType).filter(UserType.uno == data['body'].get('uno')).first()
    if usertype is None or usertype.type != 'admin':
        return {"message": f"only admin can read"}, 505

    company = db.session.query(Company).with_entities(Company.cname, Company.address, Company.keyword).all()

    if not company:
        return 'fail', 505

    result = {}

    for data in company:
        temp = {}
        temp['cname'] = data[0]
        temp['address'] = data[1]
        temp['keyword'] = data[2]
        result[data[0]] = temp

    return result, 200

def search_company(data):
    """Search Company"""
    cname_result = db.session.query(Company).with_entities(Company.cname, Company.address, Company.keyword).filter(Company.cname.like('%' + data['searchData'] + '%')).all()
    address_result = db.session.query(Company).with_entities(Company.cname, Company.address, Company.keyword).filter(Company.address.like('%' + data['searchData'] + '%')).all()
    keyword_result = db.session.query(Company).with_entities(Company.cname, Company.address, Company.keyword).filter(Company.keyword.like('%' + data['searchData'] + '%')).all()

    if not cname_result:
        cname_result = ""

    if not address_result:
        address_result = ""

    if not keyword_result:
        keyword_result = ""

    result = {}

    if cname_result != "":
        i = 0
        for data in cname_result:
            temp = {}
            temp['cname'] = data[0]
            temp['address'] = data[1]
            temp['keyword'] = data[2]
            result['cname_result' + str(i)] = temp
            i+=1

    if address_result != "":
        i = 0
        for data in address_result:
            temp = {}
            temp['cname'] = data[0]
            temp['address'] = data[1]
            temp['keyword'] = data[2]
            result['address_result' + str(i)] = temp
            i += 1

    if keyword_result != "":
        i = 0
        for data in keyword_result:
            temp = {}
            temp['cname'] = data[0]
            temp['address'] = data[1]
            temp['keyword'] = data[2]
            result['keyword_result' + str(i)] = temp
            i += 1

    return result, 200

def rank_company(data):
    """Rank Company"""
    if data['body'].get('type') == "bookmark":
        company_list = db.session.query(Company).with_entities(Company.cname,
        Company.address, Company.keyword,Company.form,Company.logo_url).order_by(desc(Company.bookmarkcnt)).all()
    elif data['body'].get('type') == "cname":
        company_list = db.session.query(Company).with_entities(Company.cname,
        Company.address, Company.keyword,Company.form,Company.logo_url).order_by((Company.cname)).all()
    else:
        company_list = db.session.query(Company).with_entities(Company.cname,
        Company.address, Company.keyword,Company.form,Company.logo_url).order_by(desc(Company.readcnt)).all()

    result = {}
    i = 0

    for company in company_list:
        if data['body'].get('f_all') == 0:
            if i < 5:
                temp = {}
                temp['cname'] = company[0]
                temp['address'] = company[1]
                temp['keyword'] = company[2]
                temp['form'] = company[3]
                temp['logo_url'] = company[4]
                result['rank' + str(i)] = temp
                i += 1
        else:
            temp = {}
            temp['cname'] = company[0]
            temp['address'] = company[1]
            temp['keyword'] = company[2]
            temp['form'] = company[3]
            temp['logo_url'] = company[4]
            result['rank' + str(i)] = temp
            i += 1

    return result, 200

def read_company(data) :
    """Read Company"""

    companies = db.session.query(Company).filter(Company.cname == data['body'].get('cname')).all()
    bookmark_cnt = db.session.query(func.count(Bookmark.id)).filter(Bookmark.cname == data['body'].get('cname')).scalar()

    if not companies:
        return 'fail', 502

    result = {}
    for company in companies:
        # Extract company data and remove unnecessary attributes
        temp = company.__dict__.copy()
        del temp['_sa_instance_state']
        del temp['cno']
        readcnt = temp['readcnt'] + 1
        del temp['readcnt']
        del temp['bookmarkcnt']
        # Update company read count and add to result dictionary
        company.bookmarkcnt = bookmark_cnt
        company.readcnt = readcnt
        db.session.commit()
        result['company'] = temp

    return {'result': result}, 200
