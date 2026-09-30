import os
import sys

# Ensure local imports work regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.togglebutton import ToggleButton

from database import LocalDatabase
from localization import get_text

class AddTransactionScreen(Screen):
    def __init__(self, db: LocalDatabase, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.trans_type = "expense"
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        lang = self.db.get_setting("language", "uz")

        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Header
        title = Label(
            text=get_text("add_transaction", lang),
            font_size='20sp',
            bold=True,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(title)

        # Type Selector (Expense / Income)
        type_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=45)

        self.btn_expense = ToggleButton(
            text=get_text("expense", lang),
            group='trans_type',
            state='down' if self.trans_type == 'expense' else 'normal',
            allow_no_selection=False
        )
        self.btn_expense.bind(on_press=lambda instance: self.set_trans_type('expense'))

        self.btn_income = ToggleButton(
            text=get_text("income", lang),
            group='trans_type',
            state='down' if self.trans_type == 'income' else 'normal',
            allow_no_selection=False
        )
        self.btn_income.bind(on_press=lambda instance: self.set_trans_type('income'))

        type_layout.add_widget(self.btn_expense)
        type_layout.add_widget(self.btn_income)
        main_layout.add_widget(type_layout)

        # Amount Input
        main_layout.add_widget(Label(text=get_text("amount", lang), size_hint_y=None, height=25, halign='left'))
        self.amount_input = TextInput(
            hint_text=get_text("amount_hint", lang),
            input_filter='float',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.amount_input)

        # Category Dropdown / Spinner
        main_layout.add_widget(Label(text=get_text("category", lang), size_hint_y=None, height=25, halign='left'))
        categories = self.db.get_categories(self.trans_type)
        cat_names = [c["name"] for c in categories] if categories else ["Select"]

        self.cat_spinner = Spinner(
            text=cat_names[0] if cat_names else "",
            values=cat_names,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.cat_spinner)

        # Currency Dropdown
        main_layout.add_widget(Label(text=get_text("currency", lang), size_hint_y=None, height=25, halign='left'))
        currencies = ["uzs", "usd", "eur", "rub"]
        default_curr = self.db.get_setting("currency", "uzs")
        self.curr_spinner = Spinner(
            text=default_curr.lower(),
            values=currencies,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.curr_spinner)

        # Additional Notes
        main_layout.add_widget(Label(text=get_text("notes", lang), size_hint_y=None, height=25, halign='left'))
        self.notes_input = TextInput(
            hint_text=get_text("notes_hint", lang),
            multiline=False,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(self.notes_input)

        # Status Message Label
        self.msg_label = Label(text="", size_hint_y=None, height=30, color=(0.2, 0.8, 0.2, 1))
        main_layout.add_widget(self.msg_label)

        # Submit Button
        submit_btn = Button(
            text=get_text("submit", lang),
            size_hint_y=None,
            height=45,
            background_color=(0.2, 0.6, 1, 1)
        )
        submit_btn.bind(on_press=self.save_transaction)
        main_layout.add_widget(submit_btn)

        self.add_widget(main_layout)

    def set_trans_type(self, trans_type):
        self.trans_type = trans_type
        categories = self.db.get_categories(self.trans_type)
        cat_names = [c["name"] for c in categories] if categories else []
        self.cat_spinner.values = cat_names
        self.cat_spinner.text = cat_names[0] if cat_names else ""

    def update_categories(self):
        categories = self.db.get_categories(self.trans_type)
        cat_names = [c["name"] for c in categories] if categories else []
        self.cat_spinner.values = cat_names
        if self.cat_spinner.text not in cat_names:
            self.cat_spinner.text = cat_names[0] if cat_names else ""

    def save_transaction(self, instance):
        lang = self.db.get_setting("language", "uz")
        amount_str = self.amount_input.text.strip()
        category = self.cat_spinner.text.strip()
        currency = self.curr_spinner.text.strip()
        notes = self.notes_input.text.strip()

        if not amount_str:
            self.msg_label.color = (1, 0.2, 0.2, 1)
            self.msg_label.text = get_text("error_invalid_amount", lang)
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            self.msg_label.color = (1, 0.2, 0.2, 1)
            self.msg_label.text = get_text("error_invalid_amount", lang)
            return

        if not category:
            self.msg_label.color = (1, 0.2, 0.2, 1)
            self.msg_label.text = get_text("error_no_category", lang)
            return

        self.db.add_transaction(
            trans_type=self.trans_type,
            amount=amount,
            currency=currency,
            source=category,
            additional_info=notes
        )

        self.amount_input.text = ""
        self.notes_input.text = ""
        self.msg_label.color = (0.2, 0.8, 0.2, 1)
        self.msg_label.text = get_text("success_add", lang)


class SettingsScreen(Screen):
    def __init__(self, db: LocalDatabase, on_language_change_callback, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.on_language_change_callback = on_language_change_callback
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        lang = self.db.get_setting("language", "uz")

        scroll = ScrollView()
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        # Header
        title = Label(
            text=get_text("settings_title", lang),
            font_size='20sp',
            bold=True,
            size_hint_y=None,
            height=35
        )
        main_layout.add_widget(title)

        # --- User Profile Section ---
        profile_header = Label(
            text=f"👤 {get_text('user_profile', lang)}",
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=30
        )
        main_layout.add_widget(profile_header)

        # Fullname
        main_layout.add_widget(Label(text=get_text("fullname", lang), size_hint_y=None, height=25))
        self.fullname_input = TextInput(
            text=self.db.get_setting("fullname", "User"),
            multiline=False,
            size_hint_y=None,
            height=35
        )
        main_layout.add_widget(self.fullname_input)

        # Gender
        main_layout.add_widget(Label(text=get_text("sex", lang), size_hint_y=None, height=25))
        current_sex = self.db.get_setting("sex", "male")
        sex_map = {"male": get_text("male", lang), "female": get_text("female", lang)}
        self.sex_spinner = Spinner(
            text=sex_map.get(current_sex, get_text("male", lang)),
            values=list(sex_map.values()),
            size_hint_y=None,
            height=35
        )
        self.sex_keys = {get_text("male", lang): "male", get_text("female", lang): "female"}
        main_layout.add_widget(self.sex_spinner)

        # Social Status
        main_layout.add_widget(Label(text=get_text("status", lang), size_hint_y=None, height=25))
        status_keys = ["employee", "student", "businessman", "unemployed"]
        current_status = self.db.get_setting("social_status", "employee")
        status_map = {k: get_text(k, lang) for k in status_keys}
        self.status_spinner = Spinner(
            text=status_map.get(current_status, get_text("employee", lang)),
            values=list(status_map.values()),
            size_hint_y=None,
            height=35
        )
        self.status_keys_reverse = {get_text(k, lang): k for k in status_keys}
        main_layout.add_widget(self.status_spinner)

        # Language Selector
        main_layout.add_widget(Label(text=get_text("language", lang), size_hint_y=None, height=25))
        lang_map = {"uz": "O'zbekcha (uz)", "en": "English (en)", "ru": "Русский (ru)"}
        current_lang = self.db.get_setting("language", "uz")
        self.lang_spinner = Spinner(
            text=lang_map.get(current_lang, lang_map["uz"]),
            values=list(lang_map.values()),
            size_hint_y=None,
            height=35
        )
        self.lang_keys_reverse = {v: k for k, v in lang_map.items()}
        main_layout.add_widget(self.lang_spinner)

        # Default Currency Selector
        main_layout.add_widget(Label(text=get_text("default_currency", lang), size_hint_y=None, height=25))
        currencies = ["uzs", "usd", "eur", "rub"]
        current_curr = self.db.get_setting("currency", "uzs")
        self.curr_spinner = Spinner(
            text=current_curr.lower(),
            values=currencies,
            size_hint_y=None,
            height=35
        )
        main_layout.add_widget(self.curr_spinner)

        # Save Profile Button
        save_btn = Button(
            text=get_text("save_profile", lang),
            size_hint_y=None,
            height=40,
            background_color=(0.2, 0.7, 0.3, 1)
        )
        save_btn.bind(on_press=self.save_profile)
        main_layout.add_widget(save_btn)

        self.profile_msg_label = Label(text="", size_hint_y=None, height=25, color=(0.2, 0.8, 0.2, 1))
        main_layout.add_widget(self.profile_msg_label)

        # --- Category Management Section ---
        cat_header = Label(
            text=f"📁 {get_text('categories_title', lang)}",
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=35
        )
        main_layout.add_widget(cat_header)

        # Category Type Toggle (Expense / Income)
        cat_type_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=35)
        self.cat_mgmt_type = getattr(self, 'cat_mgmt_type', 'expense')

        btn_cat_exp = ToggleButton(
            text=get_text("manage_expense_cats", lang),
            group='cat_mgmt_type',
            state='down' if self.cat_mgmt_type == 'expense' else 'normal',
            allow_no_selection=False
        )
        btn_cat_exp.bind(on_press=lambda inst: self.switch_cat_mgmt_type('expense'))

        btn_cat_inc = ToggleButton(
            text=get_text("manage_income_cats", lang),
            group='cat_mgmt_type',
            state='down' if self.cat_mgmt_type == 'income' else 'normal',
            allow_no_selection=False
        )
        btn_cat_inc.bind(on_press=lambda inst: self.switch_cat_mgmt_type('income'))

        cat_type_layout.add_widget(btn_cat_exp)
        cat_type_layout.add_widget(btn_cat_inc)
        main_layout.add_widget(cat_type_layout)

        # Add Category Layout
        add_cat_layout = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=35)
        self.new_cat_input = TextInput(
            hint_text=get_text("add_cat_hint", lang),
            multiline=False,
            size_hint_x=0.7
        )
        add_cat_btn = Button(
            text=get_text("add_cat_btn", lang),
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 1, 1)
        )
        add_cat_btn.bind(on_press=self.add_category)
        add_cat_layout.add_widget(self.new_cat_input)
        add_cat_layout.add_widget(add_cat_btn)
        main_layout.add_widget(add_cat_layout)

        self.cat_msg_label = Label(text="", size_hint_y=None, height=25, color=(0.2, 0.8, 0.2, 1))
        main_layout.add_widget(self.cat_msg_label)

        # Category List Widget
        self.cat_list_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.cat_list_layout.bind(minimum_height=self.cat_list_layout.setter('height'))
        main_layout.add_widget(self.cat_list_layout)

        self.refresh_cat_list()

        scroll.add_widget(main_layout)
        self.add_widget(scroll)

    def switch_cat_mgmt_type(self, cat_type):
        self.cat_mgmt_type = cat_type
        self.refresh_cat_list()

    def refresh_cat_list(self):
        self.cat_list_layout.clear_widgets()
        lang = self.db.get_setting("language", "uz")
        categories = self.db.get_categories(self.cat_mgmt_type)

        for cat in categories:
            row = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=35)
            row.add_widget(Label(text=cat["name"], size_hint_x=0.7, halign='left'))

            del_btn = Button(
                text=get_text("delete", lang),
                size_hint_x=0.3,
                background_color=(1, 0.3, 0.3, 1)
            )
            cat_id = cat["id"]
            del_btn.bind(on_press=lambda inst, cid=cat_id: self.delete_category(cid))
            row.add_widget(del_btn)

            self.cat_list_layout.add_widget(row)

    def add_category(self, instance):
        lang = self.db.get_setting("language", "uz")
        cat_name = self.new_cat_input.text.strip()
        if not cat_name:
            self.cat_msg_label.color = (1, 0.2, 0.2, 1)
            self.cat_msg_label.text = get_text("cat_empty", lang)
            return

        success = self.db.add_category(self.cat_mgmt_type, cat_name)
        if success:
            self.new_cat_input.text = ""
            self.cat_msg_label.color = (0.2, 0.8, 0.2, 1)
            self.cat_msg_label.text = get_text("cat_added", lang)
            self.refresh_cat_list()
            self.on_language_change_callback() # Re-sync category choices across screens
        else:
            self.cat_msg_label.color = (1, 0.2, 0.2, 1)
            self.cat_msg_label.text = get_text("cat_exists", lang)

    def delete_category(self, cat_id):
        lang = self.db.get_setting("language", "uz")
        self.db.delete_category(cat_id)
        self.cat_msg_label.color = (0.2, 0.8, 0.2, 1)
        self.cat_msg_label.text = get_text("cat_deleted", lang)
        self.refresh_cat_list()
        self.on_language_change_callback()

    def save_profile(self, instance):
        selected_lang = self.lang_keys_reverse.get(self.lang_spinner.text, "uz")
        selected_sex = self.sex_keys.get(self.sex_spinner.text, "male")
        selected_status = self.status_keys_reverse.get(self.status_spinner.text, "employee")
        selected_curr = self.curr_spinner.text.lower()
        fullname = self.fullname_input.text.strip()

        old_lang = self.db.get_setting("language", "uz")

        self.db.set_setting("fullname", fullname)
        self.db.set_setting("sex", selected_sex)
        self.db.set_setting("social_status", selected_status)
        self.db.set_setting("language", selected_lang)
        self.db.set_setting("currency", selected_curr)

        self.profile_msg_label.text = get_text("profile_saved", selected_lang)

        # Notify app to re-render all UI if language or settings changed
        self.on_language_change_callback()


class FinanceApp(App):
    def build(self):
        db_path = os.path.join(os.path.dirname(__file__), "finance_app.db")
        self.db = LocalDatabase(db_path=db_path)

        root = BoxLayout(orientation='vertical')

        # Screen Manager
        self.sm = ScreenManager(transition=FadeTransition())

        self.add_screen = AddTransactionScreen(db=self.db, name='add_transaction')
        self.settings_screen = SettingsScreen(db=self.db, on_language_change_callback=self.on_app_update, name='settings')

        self.sm.add_widget(self.add_screen)
        self.sm.add_widget(self.settings_screen)

        root.add_widget(self.sm)

        # Bottom Navigation Bar
        self.nav_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=2)
        self.build_nav_bar()
        root.add_widget(self.nav_bar)

        return root

    def build_nav_bar(self):
        self.nav_bar.clear_widgets()
        lang = self.db.get_setting("language", "uz")

        btn_add = Button(
            text=get_text("nav_add", lang),
            background_color=(0.2, 0.5, 0.8, 1)
        )
        btn_add.bind(on_press=lambda inst: self.switch_screen('add_transaction'))

        btn_settings = Button(
            text=get_text("nav_settings", lang),
            background_color=(0.3, 0.3, 0.3, 1)
        )
        btn_settings.bind(on_press=lambda inst: self.switch_screen('settings'))

        self.nav_bar.add_widget(btn_add)
        self.nav_bar.add_widget(btn_settings)

    def switch_screen(self, screen_name):
        self.sm.current = screen_name

    def on_app_update(self):
        # Refresh all UI components when language or settings change
        self.add_screen.build_ui()
        self.settings_screen.build_ui()
        self.build_nav_bar()

if __name__ == '__main__':
    FinanceApp().run()
