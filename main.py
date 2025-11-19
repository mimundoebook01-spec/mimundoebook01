from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import json
import os
from datetime import datetime


DATA_DIR = "data"
PRODUCTS_FILE = f"{DATA_DIR}/products.json"
CLIENTS_FILE = f"{DATA_DIR}/clients.json"
SALES_FILE = f"{DATA_DIR}/sales.json"


def load_json(file_path, default_data):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump(default_data, f)
    with open(file_path, "r") as f:
        return json.load(f)


def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


class OrderScreen(Screen):
    selected_products = ListProperty([])
    customer_name = StringProperty("")
    customer_phone = StringProperty("")
    customer_address = StringProperty("")

    def load_products(self):
        self.products = load_json(PRODUCTS_FILE, [])
        container = self.ids.products_container
        container.clear_widgets()

        for product in self.products:
            item = ProductItem(
                name=product["name"],
                price=product["price"],
                image=product["image"]
            )
            container.add_widget(item)

    def add_to_order(self, name, price):
        self.selected_products.append({"name": name, "price": price})
        self.update_order_total()

    def update_order_total(self):
        total = sum(item["price"] for item in self.selected_products)
        self.ids.total_label.text = f"Total: ${total}"

    def generate_ticket(self):
        if not self.customer_name:
            self.show_popup("Debe ingresar un nombre")
            return

        ticket = "=== TICKET VIRTUAL ===\n"
        ticket += f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        ticket += f"Cliente: {self.customer_name}\n"
        ticket += f"Teléfono: {self.customer_phone}\n"
        ticket += f"Dirección: {self.customer_address}\n\n"
        ticket += "Productos:\n"

        total = 0
        for item in self.selected_products:
            ticket += f"- {item['name']} — ${item['price']}\n"
            total += item['price']

        ticket += f"\nTotal: ${total}"

        self.show_popup(ticket)

    def show_popup(self, text):
        popup = Popup(title="Información",
                      content=Label(text=text),
                      size_hint=(0.8, 0.6))
        popup.open()


class ProductManagerScreen(Screen):
    def load_products(self):
        self.products = load_json(PRODUCTS_FILE, [])
        container = self.ids.manage_products_container
        container.clear_widgets()

        for prod in self.products:
            container.add_widget(
                Label(text=f"{prod['name']} — Precio: ${prod['price']}")
            )

    def add_product(self):
        name = self.ids.new_product_name.text
        price = float(self.ids.new_product_price.text)
        image = self.ids.new_product_image.text

        products = load_json(PRODUCTS_FILE, [])
        products.append({"name": name, "price": price, "image": image})
        save_json(PRODUCTS_FILE, products)

        self.load_products()


class ClientsScreen(Screen):
    def load_clients(self):
        self.clients = load_json(CLIENTS_FILE, [])
        container = self.ids.clients_container
        container.clear_widgets()

        for c in self.clients:
            container.add_widget(
                Label(text=f"{c['name']} — {c['phone']} — {c['favorite']}")
            )

    def add_client(self):
        name = self.ids.client_name.text
        phone = self.ids.client_phone.text
        favorite = self.ids.client_favorite.text

        clients = load_json(CLIENTS_FILE, [])
        clients.append({"name": name, "phone": phone, "favorite": favorite})
        save_json(CLIENTS_FILE, clients)

        self.load_clients()


class StatsScreen(Screen):
    def load_stats(self):
        sales = load_json(SALES_FILE, [])
        total_sales = sum(s["total"] for s in sales)
        total_orders = len(sales)

        self.ids.total_sales_label.text = f"Ventas totales: ${total_sales}"
        self.ids.total_orders_label.text = f"Pedidos realizados: {total_orders}"


class ImmanuelApp(App):
    def build(self):
        return Builder.load_file("kv/main.kv")


if __name__ == "__main__":
    ImmanuelApp().run()
