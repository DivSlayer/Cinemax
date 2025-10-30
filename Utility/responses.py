import json

from django.core.paginator import Paginator
from django.http import HttpResponse

from Utility.no_serializer import all_serializer


def paginator(arr: list, page=1, per_page=50):
    """
    @arr: The array that you want to set
    Returns a Page obj and Page range
    """
    paginator = Paginator(arr, per_page)
    page_obj = paginator.get_page(page)
    page_range = paginator.page_range
    return page_obj, page_range


def list_response(
    arr, page=1, per_page=24, small=False, item_img=False, serialize=True
):
    page_obj, page_range = paginator(arr, page, per_page)
    response = {
        "length": len(arr),
        "page": int(page),
        "has_next": page_obj.has_next(),
        "next": page_obj.next_page_number() if page_obj.has_next() else None,
        "has_prev": page_obj.has_previous(),
        "prev": page_obj.previous_page_number() if page_obj.has_previous() else None,
        "first_page": 1,
        "last_page": page_range.stop - 1,
        "datas": [
            all_serializer(obj, small=small, item_img=item_img)
            for obj in page_obj.object_list
        ]
        if serialize
        else page_obj.object_list,
    }

    return HttpResponse(json.dumps(response), content_type="application/json")


def error_response(string="something went wrong!", code=400):
    return HttpResponse(
        json.dumps(string), content_type="application/json", status=code
    )


def single_response(datas: dict | list):
    return HttpResponse(json.dumps({"result": datas}), content_type="application/json")
