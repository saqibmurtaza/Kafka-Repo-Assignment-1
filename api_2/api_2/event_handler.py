# from .database import get_session, select
# from .model import Product

# async def crud_event_handler(event):
#     operation= event.get('operation')
#     product_dict= event.get('data')
#     if operation == 'add':
#         await add_product(product_dict)
#     elif operation == 'read':
#         await read_all_products(product_dict)    
#     elif operation == 'update':
#         await delete_product(product_dict)
    
# async def add_product(data):
#     with get_session() as session:
#         product= Product(**data) # parameter data get an argument product_dict & ** unpack dict
#         await session.add(product)
#         await session.commit()
#         await session.refresh(product)
#         return {"message":"Product successfully added"}
# async def read_all_products(data):
#     with get_session() as session:
#         product= Product(**data)
#         await session.exec(select(product)).all()
# async def delete_product(data):
#     with get_session() as session:
#         product= Product(**data)
#         product_id= product.id
#         await session.delete(product_id)
#         await session.commit()
#         return {"message":"Product successfully deleted"}

# import logging
# from .database import get_session, select
# from .model import Product

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# async def crud_event_handler(event):
#     operation = event.get('operation')
#     product_dict = event.get('data')
#     logger.info(f"Handling event: {event}")

#     if operation == 'add':
#         await add_product(product_dict)
#     elif operation == 'read':
#         await read_all_products(product_dict)    
#     elif operation == 'delete':
#         await delete_product(product_dict)
#     else:
#         logger.warning(f"Unsupported operation: {operation}")

# async def add_product(data):
#     with get_session() as session:
#         try:
#             logger.info(f"Adding product: {data}")
#             product = Product(**data)  # parameter data get an argument product_dict & ** unpack dict
#             await session.add(product)
#             await session.commit()
#             await session.refresh(product)
#             logger.info("Product successfully added")
#             return {"message": "Product successfully added"}
#         except Exception as e:
#             logger.error(f"Error adding product: {e}")
#             await session.rollback()

# async def read_all_products(data):
#     with get_session() as session:
#         try:
#             logger.info(f"Reading products with filter: {data}")
#             product = Product(**data)
#             products = await session.exec(select(product)).all()
#             logger.info(f"Products retrieved: {products}")
#         except Exception as e:
#             logger.error(f"Error reading products: {e}")

# async def delete_product(data):
#     with get_session() as session:
#         try:
#             logger.info(f"Deleting product with data: {data}")
#             product = Product(**data)
#             product_id = product.id
#             await session.delete(product_id)
#             await session.commit()
#             logger.info("Product successfully deleted")
#             return {"message": "Product successfully deleted"}
#         except Exception as e:
#             logger.error(f"Error deleting product: {e}")
#             await session.rollback()
