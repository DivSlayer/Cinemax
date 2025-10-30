from Lists.forms import CreateList, CreateListItem
from Lists.models import Item, List
from Lists.serializers import ItemSerializer, ListSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer


@api_view(("GET", "POST"))
def create_item(request, uuid):
    if request.method == "POST":
        form = CreateListItem(request.POST)
        list_ins = List.objects.filter(en_name=uuid).first()
        if form.is_valid():
            form_ins = form.save(commit=False)
            form_ins.belong = list_ins
            form_ins.save()
            return Response(ItemSerializer(form_ins).data)
        else:
            return Response(form.errors, status=400)


@api_view(("POST",))
def create_list(request, uuid):
    if request.method == "POST":
        form = CreateList(request.POST)
        if form.is_valid():
            form.save()
            return Response(ListSerializer(form.instance).data)
        else:
            return Response(form.errors, status=400)


@api_view(("GET",))
def get_lists(request):
    serialized = ListSerializer(List.objects.all().order_by("done"), many=True)
    return Response(serialized.data)


@api_view(("GET", "POST", "DELETE"))
def get_item(request, uuid):
    if request.method == "GET":
        serialized = ItemSerializer(Item.objects.filter(uuid=uuid).first())
        return Response(serialized.data)
    elif request.method == "POST":
        instance = Item.objects.filter(uuid=uuid).first()
        form = CreateListItem(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return Response({"result": "Done!"})
        else:
            return Response(form.errors)
    elif request.method == "DELETE":
        instance = Item.objects.filter(uuid=uuid).first()
        instance.delete()
        return Response({"result": "Done!"})


@api_view(("GET", "POST", "DELETE"))
def item_done(request, uuid):
    item = Item.objects.filter(uuid=uuid).first()
    item.done = True
    item.save()
    return Response({"result": "done!"})


@api_view(("GET", "POST", "DELETE"))
def list_done(request, uuid):
    item = List.objects.filter(en_name=uuid).first()
    item.done = True
    item.save()
    return Response({"result": "done!"})


@api_view(("GET", "POST", "DELETE"))
def get_list(request, name):
    list_ins = List.objects.filter(en_name=name).first()
    if request.method == "GET":
        serialized = ListSerializer(list_ins)
        return Response(serialized.data)
    if request.method == "POST":
        form = CreateList(request.POST, instance=list_ins)
        if form.is_valid():
            form.save()
            return Response({"result": "Done!"})
        else:
            return Response(form.errors)
    if request.method == "DELETE":
        list_ins.delete()
        return Response({"result": "Done!"})
