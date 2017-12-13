#!/usr/bin/env python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Item, User
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('postgresql+psycopg2://lilly:12345@localhost/items_db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = User(name="John Doe", email="john.doe@gmail.com",
             picture="https://d30y9cdsu7xlg0.cloudfront.net/png/1382526-200.png")  # NOQA

session.add(user1)
session.commit()

user2 = User(name="Alicia Test", email="alicia.test@gmail.com",
             picture="https://d30y9cdsu7xlg0.cloudfront.net/png/1050260-200.png")  # NOQA

session.add(user2)
session.commit()

category1 = Category(name="Video Games",
                     image_url="https://d30y9cdsu7xlg0.cloudfront.net/png/1272719-200.png",  # NOQA
                     user_id=1)

session.add(category1)
session.commit()

category2 = Category(name="Pullover",
                     image_url="https://d30y9cdsu7xlg0.cloudfront.net/png/337101-200.png",  # NOQA
                     user_id=1)

session.add(category2)
session.commit()

category3 = Category(name="Jewelry",
                     image_url="https://d30y9cdsu7xlg0.cloudfront.net/png/1126408-200.png",  # NOQA
                     user_id=1)

session.add(category3)
session.commit()

item1 = Item(name="Titanfall 2",
             description='''Advanced, Action-Packed Gameplay –
             Whether fighting as a Pilot, the dominant force on The Frontier,
             or as a Titan, 20-foot tall war machines, Titanfall 2 provides an
             incredibly fun, fluid, and thrilling combat experience that is
             unmatched.
             Captivating Single Player Campaign – Step on to The Frontier as a
             Militia rifleman with aspirations of becoming a Pilot. Stranded
             behind enemy lines, and against overwhelming odds, you must team
             up with a veteran Vanguard-class Titan and uphold a mission you
             were never meant to carry out.
             Deeper Multiplayer Action – With six brand-new Titans, a host of
             deadly new Pilot abilities, an expanded customization system, new
             modes and much more, Titanfall 2 gives players the deeper
             Multiplayer experience they have been asking for.
             Play with Friends, or Make New Ones – The social tissue of
             Titanfall 2, Networks makes it fast and easy to play with friends
             old and new. Whether Social or Competitive, players will be able
             to create and join a variety of Networks that best suit their play
             styles and preferences.''',
             price="12.90",
             link="https://www.amazon.com/Titanfall-2-PlayStation-4/dp/B01GKGVI8U/ref=sr_1_2?s=videogames&ie=UTF8&qid=1513176760&sr=1-2&keywords=ps4%2Bgames&th=1",  # NOQA
             img_url="https://images-na.ssl-images-amazon.com/images/I/71hkOZeZQ7L._AC_SX215_.jpg",  # NOQA
             category_id=1,
             user_id=1)

session.add(item1)
session.commit()

item2 = Item(name="Video Game Sweater",
             description='''Great shirt for an Ugly Christmas sweater party.
             Xmas gift idea for son, daughter, grandson or granddaughter.
             A comfy, Soft Juniors, Youth kids printed long sleeve T-shirt.
             Santa Video Game funny Ugly Christmas Long Sleeve Shirt
             - non itchy fabric.
             WAY BETTER than a sweater! Fun Christmas gift idea.
             OUTSTANDING FABRIC QUALITY! SUPER FAST SHIPPING!
             100% MONEY BACK GUARANTEE
             Official Teestars Merchandise
             100% combed-cotton. Printed in the USA''',
             price="14.95",
             link="https://www.amazon.com/Christmas-Sweater-Holiday-Sleeve-T-Shirt/dp/B01L1M6FM2/ref=sr_1_2?ie=UTF8&qid=1513177479&sr=8-2&keywords=christmas+geek+sweater",  # NOQA
             img_url="https://images-na.ssl-images-amazon.com/images/I/61qQWksqLcL._UY999_.jpg",  # NOQA
             category_id=2,
             user_id=1)

session.add(item2)
session.commit()

item2 = Item(name="Molecule Necklace",
             description='''Dopamine Molecule necklace-925 Solid Sterling
             Silver Fine jewelry
             Chemistry jewelry collection by MOLECULE NECKLACE BRAND
             1 year warranty
             Metal Options: Solid Sterling Silver or 18K gold plated over
             925 Solid Silver''',
             price="39.90",
             link="https://www.amazon.com/Dopamine-Molecule-Necklace-Sterling-Chemistry/dp/B072FCMQSW/ref=sr_1_28?s=apparel&ie=UTF8&qid=1513178112&sr=1-28&nodeID=7147440011&psd=1&keywords=geek+jewelry+for+women",  # NOQA
             img_url="https://images-na.ssl-images-amazon.com/images/I/311IKoEDziL._AC_UL260_SR200,260_.jpg",  # NOQA
             category_id=3,
             user_id=2)

session.add(item2)
session.commit()
