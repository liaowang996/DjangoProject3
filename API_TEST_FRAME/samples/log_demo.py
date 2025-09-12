import logging

logger = logging.getLogger("logger")
logger.setLevel(10)
handler1 = logging.StreamHandler ()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler1.setFormatter(formatter)
logger.addHandler(handler1)

handler2 = logging.FileHandler("./test.log",'a',encoding='utf-8')
handler2.setLevel(10)
handler2.setFormatter(formatter)
logger.addHandler(handler2)


logger.info("hello")