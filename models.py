# models.py
from datetime import datetime
import pytz


class Vehicle:
    def __init__(self, title, owner, vehicle_type, brand, model, year, color, engine_displacement, fuel_type,
                 transmission_type, mileage, price, description, active, additional_attributes,
                 image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Logo_of_METU.svg/707px-Logo_of_METU.svg.png",
                 db=None):
        self.db = db
        self.category = "Vehicle"
        self.title = title
        self.owner = owner
        self.vehicle_type = vehicle_type
        self.brand = brand
        self.model = model
        self.year = year
        self.color = color
        self.engine_displacement = engine_displacement
        self.fuel_type = fuel_type
        self.transmission_type = transmission_type
        self.mileage = mileage
        self.price = price
        self.description = description
        self.active = active
        self.image_url = image_url
        self.date = datetime.now(pytz.timezone('Europe/Istanbul'))

        self.additional_attributes = additional_attributes if additional_attributes is not None else {}

    def save(self):
        if self.db:
            vehicle_data = {
                "category": self.category,
                "date": self.date
            }

            if self.title:
                vehicle_data["title"] = self.title
            if self.owner:
                vehicle_data["owner"] = self.owner
            if self.vehicle_type:
                vehicle_data["type"] = self.vehicle_type
            if self.brand:
                vehicle_data["brand"] = self.brand
            if self.model:
                vehicle_data["model"] = self.model
            if self.year:
                vehicle_data["year"] = self.year
            if self.color:
                vehicle_data["color"] = self.color
            if self.engine_displacement:
                vehicle_data["engine_displacement"] = self.engine_displacement
            if self.fuel_type:
                vehicle_data["fuel_type"] = self.fuel_type
            if self.transmission_type:
                vehicle_data["transmission_type"] = self.transmission_type
            if self.mileage:
                vehicle_data["mileage"] = self.mileage
            if self.price:
                vehicle_data["price"] = self.price
            if self.description:
                vehicle_data["description"] = self.description
            if self.active:
                vehicle_data["active"] = self.active
            if self.image_url:
                vehicle_data["image_url"] = self.image_url

            # Add additional attributes to the data
            vehicle_data.update(self.additional_attributes)

            self.db["items"].insert_one(vehicle_data)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class Computer:
    def __init__(self, title, owner, computer_type, brand, model, year, processor, ram, ssd, hdd, graphics_card,
                 operating_system, price, description, active, additional_attributes,
                 image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Logo_of_METU.svg/707px-Logo_of_METU.svg.png",
                 db=None):
        self.db = db
        self.category = "Computer"
        self.title = title
        self.owner = owner
        self.computer_type = computer_type
        self.brand = brand
        self.model = model
        self.year = year
        self.processor = processor
        self.ram = ram
        self.ssd = ssd
        self.hdd = hdd
        self.graphics_card = graphics_card
        self.operating_system = operating_system
        self.price = price
        self.description = description
        self.active = active
        self.image_url = image_url
        self.date = datetime.now(pytz.timezone('Europe/Istanbul'))

        self.additional_attributes = additional_attributes if additional_attributes is not None else {}


    def save(self):
        if self.db:
            computer_data = {
                "category": self.category,
                "date": self.date
            }

            if self.title:
                computer_data["title"] = self.title
            if self.owner:
                computer_data["owner"] = self.owner
            if self.computer_type:
                computer_data["type"] = self.computer_type
            if self.brand:
                computer_data["brand"] = self.brand
            if self.model:
                computer_data["model"] = self.model
            if self.year:
                computer_data["year"] = self.year
            if self.processor:
                computer_data["processor"] = self.processor
            if self.ram:
                computer_data["ram"] = self.ram
            if self.graphics_card:
                computer_data["graphics_card"] = self.graphics_card
            if self.operating_system:
                computer_data["operating_system"] = self.operating_system
            if self.price:
                computer_data["price"] = self.price
            if self.description:
                computer_data["description"] = self.description
            if self.active:
                computer_data["active"] = self.active
            if self.image_url:
                computer_data["image_url"] = self.image_url
            if self.ssd and self.hdd:
                computer_data["storage"] = {"SSD": self.ssd, "HDD": self.hdd}
            elif self.ssd:
                computer_data["storage"] = {"SSD": self.ssd}
            elif self.hdd:
                computer_data["storage"] = {"HDD": self.hdd}

            # Add additional attributes to the data
            computer_data.update(self.additional_attributes)

            self.db["items"].insert_one(computer_data)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class Phone:
    def __init__(self, title, owner, brand, model, year, operating_system, processor, ram, storage,
                 camera_specifications, battery_capacity, price, description, active, additional_attributes,
                 image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Logo_of_METU.svg/707px-Logo_of_METU.svg.png",
                 db=None):
        self.db = db
        self.category = "Phone"
        self.title = title
        self.owner = owner
        self.brand = brand
        self.model = model
        self.year = year
        self.operating_system = operating_system
        self.processor = processor
        self.ram = ram
        self.storage = storage
        self.camera_specifications = camera_specifications
        self.battery_capacity = battery_capacity
        self.price = price
        self.description = description
        self.active = active
        self.image_url = image_url
        self.date = datetime.now(pytz.timezone('Europe/Istanbul'))

        self.additional_attributes = additional_attributes if additional_attributes is not None else {}

    def save(self):
        if self.db:
            phone_data = {
                "category": self.category,
                "date": self.date
            }

            if self.title:
                phone_data["title"] = self.title
            if self.owner:
                phone_data["owner"] = self.owner
            if self.brand:
                phone_data["brand"] = self.brand
            if self.model:
                phone_data["model"] = self.model
            if self.year:
                phone_data["year"] = self.year
            if self.operating_system:
                phone_data["operating_system"] = self.operating_system
            if self.processor:
                phone_data["processor"] = self.processor
            if self.ram:
                phone_data["ram"] = self.ram
            if self.storage:
                phone_data["storage"] = self.storage
            if self.camera_specifications:
                phone_data["camera_specifications"] = self.camera_specifications
            if self.battery_capacity:
                phone_data["battery_capacity"] = self.battery_capacity
            if self.price:
                phone_data["price"] = self.price
            if self.description:
                phone_data["description"] = self.description
            if self.active:
                phone_data["active"] = self.active
            if self.image_url:
                phone_data["image_url"] = self.image_url


            # Add additional attributes to the data
            phone_data.update(self.additional_attributes)

            self.db["items"].insert_one(phone_data)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class PrivateLesson:
    def __init__(self, title, owner, tutor_name, first_lesson, second_lesson, third_lesson, location, duration, price,
                 description, active, additional_attributes=None,
                 image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Logo_of_METU.svg/707px-Logo_of_METU.svg.png",
                 db=None):
        self.db = db
        self.category = "Private Lesson"
        self.title = title
        self.owner = owner
        self.tutor_name = tutor_name
        self.first_lesson = first_lesson
        self.second_lesson = second_lesson
        self.third_lesson = third_lesson
        self.location = location
        self.duration = duration
        self.price = price
        self.description = description
        self.active = active
        self.image_url = image_url
        self.date = datetime.now(pytz.timezone('Europe/Istanbul'))


        self.additional_attributes = additional_attributes if additional_attributes is not None else {}

    def save(self):
        if self.db:
            private_lesson_data = {
                "category": self.category,
                "date": self.date
            }

            if self.title:
                private_lesson_data["title"] = self.title
            if self.owner:
                private_lesson_data["owner"] = self.owner
            if self.tutor_name:
                private_lesson_data["tutor_name"] = self.tutor_name
            if self.first_lesson:
                private_lesson_data["first_lesson"] = self.first_lesson
            if self.second_lesson:
                private_lesson_data["second_lesson"] = self.second_lesson
            if self.third_lesson:
                private_lesson_data["third_lesson"] = self.third_lesson
            if self.location:
                private_lesson_data["location"] = self.location
            if self.duration:
                private_lesson_data["duration"] = self.duration
            if self.price:
                private_lesson_data["price"] = self.price
            if self.description:
                private_lesson_data["description"] = self.description
            if self.active:
                private_lesson_data["active"] = self.active
            if self.image_url:
                private_lesson_data["image_url"] = self.image_url

            # Add additional attributes to the data
            private_lesson_data.update(self.additional_attributes)

            self.db["items"].insert_one(private_lesson_data)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
