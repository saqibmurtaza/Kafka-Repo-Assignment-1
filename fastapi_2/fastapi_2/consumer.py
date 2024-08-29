    # from aiokafka import AIOKafkaConsumer
    # from aiokafka.errors import KafkaConnectionError
    # import logging, asyncio
    # from .database import engine, Session
    # from .model import Product
    # from fastapi_2.product_pb2 import ProductEvent

    # logging.basicConfig(level=logging.INFO)
    # logger = logging.getLogger(__name__)

    # async def start_consumer(
    #                 topic, 
    #                 bootstrap_server, consumer_group_id
    #                 ):
    #     consumer = AIOKafkaConsumer(
    #                 topic, 
    #                 bootstrap_servers=bootstrap_server, 
    #                 group_id=consumer_group_id
    #                 )
    #     # Retry mechanism to keep up the consumer
    #     while True:
    #         try:
    #             await consumer.start()
    #             logging.info('CONSUMER STARTED')
    #             break
    #         except KafkaConnectionError as e:
    #             logging.error(f'CONSUMER STARTUP FAILED {e}, Retry in 5 seconds')
    #             await asyncio.sleep(5)
            
    #     try:
    #         async for message in consumer:
    #             logger.info(f"Received message: {message.value}")
    #             product_event_proto = ProductEvent()
    #             product_event_proto.ParseFromString(message.value)

    #             logging.info(f"Operation: {product_event_proto.operation}")
    #             logging.info(f"Product Data Proto: {product_event_proto.data}")

    #             operation = product_event_proto.operation
    #             product_data_proto = product_event_proto.data

    #             with Session(engine) as session:
    #                 if operation == "add":
    #                     product_id = product_data_proto.id
    #                     if product_id == 0:
    #                         logging.warning("Received product with id=0, attempting to auto-generate id")
                        
    #                     product = Product(
    #                         id=product_id if product_id != 0 else None,  # Let the database generate id if it's 0
    #                         product_name=product_data_proto.product_name,
    #                         description=product_data_proto.description,
    #                         price=product_data_proto.price
    #                     )
                        
    #                     try:
    #                         session.add(product)
    #                         session.commit()
    #                         session.refresh(product)
    #                         logging.info(f"ADDED_PRODUCT: {product}")
                            
    #                     except Exception as e:
    #                         session.rollback()
    #                         logging.error(f"FAILED_TO_ADD_PRODUCT: {product}, ERROR: {str(e)}")
    #                 elif operation == "delete":
    #                     product_id = product_data_proto.id
    #                     product = session.get(Product, product_id)
    #                     if product:
    #                         session.delete(product)
    #                         session.commit()
    #                         logging.info(f"DELETED PRODUCT_OF_ID: {product_id}")
    #                     else:
    #                         logging.warning(f"PRODUCT_WITH_ID: {product_id} NOT_FOUND_TO_DELETE")

    #                 elif operation == "read":
    #                     product_id = product_data_proto.id
    #                     product = session.get(Product, product_id)
    #                     if product:
    #                         logging.info(f"READ_PRODUCT: {product}")
    #                     else:
    #                         logging.warning(f"PRODUCT_ID: {product_id} NOT_FOUND")

    #                 elif operation == "update":
    #                     product_id = product_data_proto.id
    #                     product = session.get(Product, product_id)
    #                     if product:
    #                         product.product_name = product_data_proto.product_name
    #                         product.description = product_data_proto.description
    #                         product.price = product_data_proto.price
    #                         session.commit()
    #                         session.refresh(product)
    #                         logging.info(f"UPDATED_PRODUCT_INFO: {product}")
    #                     else:
    #                         logging.warning(f"PRODUCT_ID: {product_id} NOT_FOUND_TO_UPDATE")

    #     except asyncio.CancelledError:
    #         logger.info("CONSUMER_TASK_CANCELLED")
    #     except Exception as e:
    #         logger.error(f"ERROR_IN_PROCESSING_MSSG: {message.value}, ERROR: {str(e)}")
    #     finally:
    #         await consumer.stop()

    from aiokafka import AIOKafkaConsumer
    from aiokafka.errors import KafkaConnectionError
    import logging, asyncio
    from sqlmodel import select
    from .database import engine, Session
    from .model import Product
    from fastapi_2.product_pb2 import ProductEvent

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    async def start_consumer(
            topic, 
            bootstrap_server, 
            consumer_group_id
    ):
        consumer = AIOKafkaConsumer(
                    topic, 
                    bootstrap_servers=bootstrap_server, 
                    group_id=consumer_group_id
                    )
        # Retry mechanism to keep up the consumer
        while True:
            try:
                await consumer.start()
                logging.info('CONSUMER STARTED')
                break
            except KafkaConnectionError as e:
                logging.error(f'CONSUMER STARTUP FAILED {e}, Retry in 5 seconds')
                await asyncio.sleep(5)
            
        try:
            async for message in consumer:
                logger.info(f"Received message: {message.value}")
                product_event_proto = ProductEvent()
                product_event_proto.ParseFromString(message.value)

                logging.info(f"Operation: {product_event_proto.operation}")
                logging.info(f"Product Data Proto: {product_event_proto.data}")

                operation = product_event_proto.operation
                product_data_proto = product_event_proto.data

                with Session(engine) as session:
                    if operation == "add":
                        product_id = product_data_proto.id
                        if product_id == 0:
                            logging.warning("Received product with id=0, attempting to auto-generate id")
                        
                        product = Product(
                            id=product_id if product_id != 0 else None,  # Let the database generate id if it's 0
                            product_name=product_data_proto.product_name,
                            description=product_data_proto.description,
                            price=product_data_proto.price
                        )
                        
                        try:
                            session.add(product)
                            session.commit()
                            session.refresh(product)
                            logging.info(f"ADDED_PRODUCT: {product}")
                            
                        except Exception as e:
                            session.rollback()
                            logging.error(f"FAILED_TO_ADD_PRODUCT: {product}, ERROR: {str(e)}")
                    elif operation == "delete":
                        product_id = product_data_proto.id
                        product = session.get(Product, product_id)
                        if product:
                            session.delete(product)
                            session.commit()
                            logging.info(f"DELETED PRODUCT_OF_ID: {product_id}")
                        else:
                            logging.warning(f"PRODUCT_WITH_ID: {product_id} NOT_FOUND_TO_DELETE")

                    elif operation == "read":
                        product_id = product_data_proto.id
                        product = session.get(Product, product_id)
                        if product:
                            logging.info(f"READ_PRODUCT: {product}")
                        else:
                            logging.warning(f"PRODUCT_ID: {product_id} NOT_FOUND")

                    elif operation == "update":
                        product_id = product_data_proto.id
                        product = session.get(Product, product_id)
                        if product:
                            product.product_name = product_data_proto.product_name
                            product.description = product_data_proto.description
                            product.price = product_data_proto.price
                            session.commit()
                            session.refresh(product)
                            logging.info(f"UPDATED_PRODUCT_INFO: {product}")
                    
                        else:
                            logging.warning(f"PRODUCT_ID: {product_id} NOT_FOUND_TO_UPDATE")

                    elif operation == "list":
                            # Fetch all products from the database
                            products = session.exec(select(Product)).all()
                            logging.info(f"RETRIEVED_PRODUCTS: {products}")



        except asyncio.CancelledError:
            logger.info("CONSUMER_TASK_CANCELLED")
        except Exception as e:
            logger.error(f"ERROR_IN_PROCESSING_MSSG: {message.value}, ERROR: {str(e)}")
        finally:
            await consumer.stop()
