import logging 

from typing import List, Union
from urllib.parse import urljoin
from uuid import UUID
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from fastapi import HTTPException, Depends
from fastapi import status as http_status

from sqlalchemy.orm import Session

from src.config.config import BASE_URL, RETRY_COUNT, RETRY_INTERVAL_SECS, IMAGES_DOWNLOAD_PATH
from src.products.schemas import Product, ListQuery
from src.utils.image_downloader import save_image_local
from src.db import crud, models, schemas

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

async def get_html(url: str, proxy_url: str, 
    retry_interval: int, retry_count: int ) -> BeautifulSoup:
    attempt = 0
    proxy = None
    if proxy_url != "":
        proxy = proxy_url
    while attempt < retry_count:
        async with ClientSession() as session:
            async with session.get(url, proxy=proxy) as response:
                text = await response.text()

                if response.status == 200:
                    html = BeautifulSoup(markup=text, features="lxml")
                    return html
                elif response.status == 500:
                    await asyncio.sleep(retry_interval)
                
                raise HTTPException(status_code=http_status.HTTP_501_NOT_IMPLEMENTED,
                            detail=f"Scraper didn't succeed in getting data:\n"
                                f"\turl: {url}\n"
                                f"\tstatus code: {response.status}\n"
                                f"\tresponse text: {text}")
        attempt+=1

def parse_products(html: BeautifulSoup) -> List[schemas.ProductDetails]:
    products = [] 
    prod_content = html.select(".product-inner")
    for element in prod_content:
        price = 0.0
        img_url = ""
        title = ""
        pid = ""
        ele_thumbnail = element.select(".mf-product-thumbnail a img.attachment-woocommerce_thumbnail")
        if ele_thumbnail:
            img_url = ele_thumbnail[0]['data-lazy-src']
        ele_price = element.select(".mf-product-price-box .price .amount bdi")
        if ele_price:
            price = ele_price[0].text[1:]
        ele_title = element.select(".mf-product-price-box .footer-button .addtocart-buynow-btn a")
        if ele_title:
            title = ele_title[0]['data-title']
        ele_pid = element.select(".mf-product-price-box .footer-button .addtocart-buynow-btn a")
        if not ele_pid:
            continue
        pid = ele_pid[0]['data-product_id']

        products.append(schemas.ProductDetails(image_url=img_url, title=title, price=price, pid=pid))
    return products

async def fetch_product_details(data: ListQuery) -> List[schemas.ProductDetails]:
    url = BASE_URL
    retry_count = RETRY_COUNT
    retry_interval = RETRY_INTERVAL_SECS

    if data.pages == 0:
        return []
    
    entrypoint_page = await get_html(url, data.proxy_url, retry_count, retry_interval)
    product_details = parse_products(html=entrypoint_page)

    if data.pages == 1:
        return product_details

    page = 2
    while page <= data.pages:
        url = f"{BASE_URL}page/{page}/"
        page_html = await get_html(url, data.proxy_url, retry_count, retry_interval)
        new_product_details = parse_products(html=page_html)
        if not new_product_details:
            break
        product_details += new_product_details
        page += 1

    return product_details

def save_product_details(data: List[schemas.ProductDetails],db: Session) -> List[Product]:
    folder_path = IMAGES_DOWNLOAD_PATH
    products = [] 
    for product in data:
        prd_db = crud.get_product(db, product.pid)
        prd_resp = prd_db
        if not prd_db:
            filepath = "{}\{}.png".format(folder_path, product.pid)
            save_image_local(filepath, product.image_url)
            product.image_path_local = filepath
            prd_resp = crud.create_product(db, product)
        elif prd_db.price!=product.price:
            prd_resp = crud.update_product(db, product.pid, product)
        products.append(Product(name=prd_resp.title, price=prd_resp.price, image_path=prd_resp.image_path))
    return products

async def get_products(data: ListQuery, task_uuid: UUID, db: Session) -> List[Product]:
    logger.info("Getting products for request id: {}".format(task_uuid))
    crud.create_task(db, task_uuid)
    product_details = await fetch_product_details(data)
    products = save_product_details(product_details, db)
    logger.info("Fetched {} products for request id: {}".format(len(products), task_uuid))
    crud.update_task(db, task_uuid=task_uuid, task=models.Tasks(status="Success", result_count=len(products)))
    return products

def get_task(task_uuid: UUID, db: Session):
    return crud.get_task(db, task_uuid)