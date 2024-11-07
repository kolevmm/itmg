from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Settings, CompanyInfo, BankAccount
from flask_login import login_required

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def manage_settings():
    settings = Settings.query.first()
    # Ако няма съществуващ запис за настройки, създаваме такъв
    if settings is None:
        settings = Settings(offer_validity=30, tax_rate=20.0, payment_terms="Стандартни условия")
        db.session.add(settings)
        db.session.commit()

    company_info = CompanyInfo.query.first()
    if company_info is None:
        company_info = CompanyInfo(company_name="", tax_number="", address="", phone="", email="")
        db.session.add(company_info)
        db.session.commit()
    bank_accounts = BankAccount.query.all()

    if request.method == 'POST':
        # Актуализиране на настройките от формуляра
        settings.offer_validity = request.form.get('offer_validity')
        settings.tax_rate = request.form.get('tax_rate')
        settings.payment_terms = request.form.get('payment_terms')
        
        # Актуализиране на информацията за компанията
        company_info.company_name = request.form.get('company_name')
        company_info.tax_number = request.form.get('tax_number')
        company_info.address = request.form.get('address')
        company_info.phone = request.form.get('phone')

        # Записване на промените
        db.session.commit()
        flash('Настройките бяха успешно актуализирани!', 'success')
        return redirect(url_for('settings.manage_settings'))

    return render_template('settings.html', settings=settings, company_info=company_info, bank_accounts=bank_accounts)



@settings_bp.route('/add_bank_account', methods=['POST'])
@login_required
def add_bank_account():
    account_name = request.form.get('bank_name')  # Името на полето във формата може да остане 'bank_name'
    iban = request.form.get('iban')
    company_info = CompanyInfo.query.first()
    # Създаване на новата банкова сметка с правилното име на полето
    new_account = BankAccount(account_name=account_name, iban=iban, company_id=company_info.id)
    db.session.add(new_account)
    db.session.commit()

    flash('Новата банкова сметка беше успешно добавена!', 'success')
    return redirect(url_for('settings.manage_settings'))

