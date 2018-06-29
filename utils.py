from authApp.models import City
from avtoportal.models import CarPropertyMark, CarPropertyModel, CarPropertyGen, Car, ColorList, CarBody, PaintElement
import json
from datetime import datetime
from django.template.loader import render_to_string
from django.middleware import csrf
from .models import SaveFilter, UserSaveFilter
import urllib

class Filter():

    paramsForFilter = None
    paramsForModel = None
    paramsForMulti = None
    custom_params = None
    countSubProp = 0

    def renderStockFilter(self,
                            request,
                            custom_params={}):
        self.custom_params = custom_params
        self.paramsForFilter = {}

        renderData = {"csrf_token": csrf.get_token(request)}
        renderData['main_area'] = {"model_filter": None, "property": None}
        model_filter_count = 1
        renderData['main_area']['model_filter_count'] = model_filter_count
        renderData['main_area']['model_filter'] = []
        requestDataModel = []
        getData = {"mark": [], "model": [], "gen": []}
        getData_modelByMark = []
        getData_genByModel = []

        for modelIndex in range(0, model_filter_count):
            if "mark_"+str(modelIndex) in request.GET:
                if request.GET["mark_"+str(modelIndex)] is not None and request.GET["mark_"+str(modelIndex)].isdigit():
                    requestDataInd = {"mark": None, "model": None, "gen": None}
                    requestDataInd['mark'] = request.GET["mark_"+str(modelIndex)]
                    getData_modelByMark.append(int(request.GET["mark_"+str(modelIndex)]))
                    if "model_"+str(modelIndex) in request.GET:
                        if request.GET["model_"+str(modelIndex)] is not None and request.GET["model_"+str(modelIndex)].isdigit():
                            requestDataInd['model'] = request.GET["model_"+str(modelIndex)]
                            # getData_genByModel.append(int(request.GET["model_"+str(modelIndex)]))
                            # if "gen_"+str(modelIndex) in request.GET:
                            #     if request.GET["gen_"+str(modelIndex)] is not None and request.GET["gen_"+str(modelIndex)].isdigit():
                            #         requestDataInd['gen'] = request.GET["gen_"+str(modelIndex)]

                    requestDataModel.append(requestDataInd)
            if "mark_"+str(modelIndex) in custom_params:
                if custom_params["mark_"+str(modelIndex)] is not None and custom_params["mark_"+str(modelIndex)].isdigit():
                    requestDataInd = {"mark": None, "model": None, "gen": None}
                    requestDataInd['mark'] = custom_params["mark_"+str(modelIndex)]
                    getData_modelByMark.append(int(custom_params["mark_"+str(modelIndex)]))
                    if "model_"+str(modelIndex) in custom_params:
                        if custom_params["model_"+str(modelIndex)] is not None and custom_params["model_"+str(modelIndex)].isdigit():
                            requestDataInd['model'] = custom_params["model_"+str(modelIndex)]
                            # getData_genByModel.append(int(custom_params["model_"+str(modelIndex)]))
                            # if "gen_"+str(modelIndex) in custom_params:
                            #     if custom_params["gen_"+str(modelIndex)] is not None and custom_params["gen_"+str(modelIndex)].isdigit():
                            #         requestDataInd['gen'] = custom_params["gen_"+str(modelIndex)]

                    requestDataModel.append(requestDataInd)

        try:
            get_mark = CarPropertyMark.objects.all().order_by("title")
        except:
            get_mark = []

        for mark in get_mark:
            getData['mark'].append({"id": mark.id, "name": mark.title, "object": mark})

        if len(getData_modelByMark) > 0:
            try:
                get_model = CarPropertyModel.objects.filter(mark_id__in=getData_modelByMark).order_by("title")
            except:
                get_model = {}
            for model in get_model:
                getData['model'].append({"id": model.id, "name": model.title, "mark": model.mark.id, "object": model})

        # if len(getData_genByModel) > 0:
        #     try:
        #         get_gen = CarPropertyGen.objects.filter(model_id__in=getData_genByModel).order_by("title")
        #     except:
        #         get_gen = {}
        #
        #     for gen in get_gen:
        #         getData['gen'].append({"id": gen.id, "name": gen.title, "model": gen.model.id, "object": gen})



        hasModelFilter = False
        for modelIndex in range(0, model_filter_count):
            returnData = {"mark": [], "model": [], "is_active": False}
            for mark in getData['mark']:
                returnMark = {}
                returnMark['id'] = mark['id']
                returnMark['name'] = mark['name']
                returnMark['is_active'] = False
                returnMark['obj'] = mark
                try:
                    checkDataIndex = requestDataModel[modelIndex]
                except:
                    checkDataIndex = None
                if checkDataIndex is not None:
                    if requestDataModel[modelIndex]['mark'] == str(returnMark['id']):
                        hasModelFilter = True
                        returnMark['is_active'] = True
                        returnData['is_active'] = True
                        for model in getData['model']:
                            # print(str(model['mark'])+"___"+str(requestDataModel[modelIndex]['mark']))
                            if int(model['mark']) == int(requestDataModel[modelIndex]['mark']):
                                returnModel = {}
                                returnModel['id'] = model['id']
                                returnModel['mark_id'] = model['mark']
                                returnModel['name'] = model['name']
                                returnModel['is_active'] = False
                                returnModel['obj'] = model
                                if "model" in requestDataModel[modelIndex]:
                                    if requestDataModel[modelIndex]['model'] == str(returnModel['id']):
                                        returnModel['is_active'] = True
                                        # for gen in getData['gen']:
                                        #     if int(gen['model']) == int(requestDataModel[modelIndex]['model']):
                                        #         returnGen = {}
                                        #         returnGen['id'] = gen['id']
                                        #         returnGen['name'] = gen['name']
                                        #         returnGen['is_active'] = False
                                        #         returnGen['obj'] = gen
                                        #         if "gen" in requestDataModel[modelIndex]:
                                        #             if requestDataModel[modelIndex]['gen'] == str(returnGen['id']):
                                        #                 returnGen['is_active'] = True
                                        #         returnData['gen'].append(returnGen)
                                    returnData['model'].append(returnModel)
                returnData['mark'].append(returnMark)
            renderData['main_area']['model_filter'].append(returnData)

        if hasModelFilter is True:
            self.paramsForModel = []
            # self.paramsForFilter['mark_id__in'] = []
            # self.paramsForFilter['model_id__in'] = []
            # self.paramsForFilter['gen_id__in'] = []
            for model_filter in renderData['main_area']['model_filter']:
                if model_filter['is_active'] is True:
                    paramItems = {'mark_id__in': [], "model_id__in": []}
                    for mark in model_filter['mark']:
                        if mark['is_active'] is True:
                            paramItems['mark_id__in'].append(mark['id'])
                    model_obj = None
                    for model in model_filter['model']:
                        if model['is_active'] is True:
                            paramItems['model_id__in'].append(model['id'])
                            model_obj = model['obj']
                    if model_obj is None:
                        for model in model_filter['model']:
                            paramItems['model_id__in'].append(model['id'])
                    # if model_filter['gen'] is not None:
                    #     for gen in model_filter['gen']:
                    #         if gen['is_active'] is True:
                    #             paramItems['gen_id__in'].append(gen['id'])
                    #
                    # if not len(paramItems['gen_id__in']) > 0:
                    #     del paramItems['gen_id__in']
                    self.paramsForModel.append(paramItems)
        renderData['main_area']['property'] = []

        nowDate = datetime.now()
        renderData['main_area']['property'].append(
            self.getFilterFieldsRange('year', request, 1890, nowDate.year, "select_range"))
        renderData['main_area']['property'].append(self.getFilterFieldsRange('mileage', request, 0, 999999))

        getFields = [
            "engine",
        ]
        for fields in getFields:
            get_field = self.getFilterFields(fields, request)
            if get_field is not None:
                renderData['main_area']['property'].append(get_field)

        renderData['main_area']['property'].append(
            self.getFilterFieldsRange('dvs', request, '0.1', '10', "select_range_dvs"))

        getFields = [
            "transmission",
            "drive_type",
        ]
        for fields in getFields:
            get_field = self.getFilterFields(fields, request)
            if get_field is not None:
                renderData['main_area']['property'].append(get_field)

        renderData['main_area']['property'].append(self.getFilterFields('body', request, 'multi_select'))
        renderData['main_area']['property'].append(self.getFilterFieldsInput('vin', request))

        getFields = [
            "has_sell",
            "has_top",
        ]
        for fields in getFields:
            get_field = self.getFilterFields(fields, request)
            if get_field is not None:
                renderData['main_area']['property'].append(get_field)


        self.dateToParam(renderData['main_area']['property'])

        template_path = "avtoportal/template_release/filter/filter_mini.html"

        return render_to_string(template_path, renderData)

    def renderFilter(self,
                     request,
                     city_area=True,
                     new_or_use=True,
                     new_or_use_default=None,
                     main_area=True,
                     main_area__model_filter=True,
                     main_area__model_filter__count=5,
                     main_area__property=True,
                     sub_area=True,
                     sub_area__main=True,
                     sub_area__defend=True,
                     sub_area__soft=True,
                     sub_area__multi=True,
                     sub_area__other=True,
                     ads_count=True,
                     save_search=True,
                     statistics=False,
                     statistics_seller=False,
                     dateTo=None,
                     dateFrom=None,
                     statisticsType=None,
                     nds_in_price=False,
                     clear_filter_link="/catalog/",
                     custom_params={},
                     filter_style="old"):

        self.custom_params = custom_params
        renderData = {"search_city": None, "new_or_use": None, "main_area": None, "sub_area": None, "ads_count": None,
                      "statistics_seller": statistics_seller, "statistics": None,
                      "save_search": None, "csrf_token": csrf.get_token(request),
                      "dateTo": dateTo, "dateFrom": dateFrom, "statisticsType": statisticsType, "nds_in_price_fields": False}
        renderData['clear_filter_link'] = clear_filter_link
        obj_car = Car()
        self.paramsForFilter = {}

        if statistics is not False:
            renderData['statistics'] = {"statisticsDateStart": "", "statisticsDateEnd": "", "showSelfCars": False}
            if "statisticsDateStart" in request.GET or "statisticsDateStart" in custom_params:
                renderData['statistics']['statisticsDateStart'] = request.GET['statisticsDateStart']
            if "statisticsDateEnd" in request.GET or "statisticsDateEnd" in custom_params:
                renderData['statistics']['statisticsDateEnd'] = request.GET['statisticsDateEnd']
            if "showSelfCars" in request.GET or "showSelfCars" in custom_params:
                renderData['statistics']['showSelfCars'] = True
                self.paramsForFilter['author_id'] = request.user.id

        if nds_in_price is True and main_area is True:
            renderData['nds_in_price_fields'] = True
            if "nds_in_price" in request.GET or "nds_in_price" in custom_params:
                renderData['nds_in_price'] = True
                self.paramsForFilter['nds_in_price'] = True

        if not 'search_city' in request.session:
            request.session['search_city'] = json.dumps([])

        if city_area is True:
            renderData['search_city'] = None

            if "search_city" in request.GET:
                city_id = []
                for city in request.GET.getlist('search_city'):
                    city_id.append(city)
                    if city == "all":
                        city_id = "all"
                        break
                if city_id is not "all":
                    try:
                        get_city = City.objects.filter(id__in=city_id)
                    except:
                        get_city = None

                    if get_city is not None:
                        renderData['search_city'] = []
                        for city in get_city:
                            renderData['search_city'].append({"name": city.name, "id": city.id})

                        request.session['search_city'] = json.dumps(renderData['search_city'])
                else:
                    request.session['search_city'] = json.dumps([{"name": "Все города", "id": city_id}])

            if "search_city" in request.session and renderData['search_city'] is None:
                if request.session['search_city'] is not None:
                    search_city = json.loads(request.session['search_city'])
                    renderData['search_city'] = search_city

            if renderData['search_city'] is None:
                try:
                    default_city = City.objects.get(name="Москва")
                except:
                    default_city = None

                if default_city is not None:
                    renderData['search_city'] = [{"name": default_city.name, "id": default_city.id}]
                else:
                    renderData['search_city'] = []
                request.session['search_city'] = json.dumps(renderData['search_city'])

        cityIDForFilter = None
        cityIDForFilter = []
        if renderData['search_city'] is not None:
            for cityID in renderData['search_city']:
                if cityID['id'] != "all":
                    cityIDForFilter.append(cityID['id'])
        if len(cityIDForFilter) > 0:
            self.paramsForFilter['author__profile__from_city_id__in'] = cityIDForFilter

        if new_or_use is True:
            renderData['new_or_use'] = [
                {"id": "all", "title": "Все", 'active': True},
                {"id": "use", "title": "С пробегом", 'active': False},
                {"id": "new", "title": "Новые", 'active': False}
            ]


            if "new_or_use" in request.GET:
                for ind, nou_item in enumerate(renderData['new_or_use']):
                    if nou_item['id'] == request.GET['new_or_use']:
                        renderData['new_or_use'][ind]['active'] = True
                    else:
                        renderData['new_or_use'][ind]['active'] = False
            if "nds_in_price" in custom_params:
                for ind, nou_item in enumerate(renderData['new_or_use']):
                    if nou_item['id'] == custom_params['new_or_use']:
                        renderData['new_or_use'][ind]['active'] = True
                    else:
                        renderData['new_or_use'][ind]['active'] = False



        if new_or_use is not True and new_or_use_default is not None:
            self.paramsForFilter['new_or_use'] = new_or_use_default

        if renderData['new_or_use'] is not None:
            for nou in renderData['new_or_use']:
                if nou['active'] is True:
                    if nou['id'] == "new":
                        self.paramsForFilter['new_or_use'] = "NEW"
                    elif nou['id'] == "use":
                        self.paramsForFilter['new_or_use'] = "USE"

        if main_area is True:
            renderData['main_area'] = {"model_filter": None, "property": None}
            if main_area__model_filter is True:
                model_filter_count = int(main_area__model_filter__count)
                renderData['main_area']['model_filter_count'] = model_filter_count
                renderData['main_area']['model_filter'] = []#{"mark": [], "model": [], "gen": []}
                requestDataModel = []
                getData = {"mark": [], "model": [], "gen": []}
                getData_modelByMark = []
                getData_genByModel = []

                for modelIndex in range(0, model_filter_count):
                    if "mark_"+str(modelIndex) in request.GET:
                        if request.GET["mark_"+str(modelIndex)] is not None and request.GET["mark_"+str(modelIndex)].isdigit():
                            requestDataInd = {"mark": None, "model": None, "gen": None}
                            requestDataInd['mark'] = request.GET["mark_"+str(modelIndex)]
                            getData_modelByMark.append(int(request.GET["mark_"+str(modelIndex)]))
                            if "model_"+str(modelIndex) in request.GET:
                                if request.GET["model_"+str(modelIndex)] is not None and request.GET["model_"+str(modelIndex)].isdigit():
                                    requestDataInd['model'] = request.GET["model_"+str(modelIndex)]
                                    getData_genByModel.append(int(request.GET["model_"+str(modelIndex)]))
                                    if "gen_"+str(modelIndex) in request.GET:
                                        if request.GET["gen_"+str(modelIndex)] is not None and request.GET["gen_"+str(modelIndex)].isdigit():
                                            requestDataInd['gen'] = request.GET["gen_"+str(modelIndex)]

                            requestDataModel.append(requestDataInd)
                    if "mark_"+str(modelIndex) in custom_params:
                        if custom_params["mark_"+str(modelIndex)] is not None and custom_params["mark_"+str(modelIndex)].isdigit():
                            requestDataInd = {"mark": None, "model": None, "gen": None}
                            requestDataInd['mark'] = custom_params["mark_"+str(modelIndex)]
                            getData_modelByMark.append(int(custom_params["mark_"+str(modelIndex)]))
                            if "model_"+str(modelIndex) in custom_params:
                                if custom_params["model_"+str(modelIndex)] is not None and custom_params["model_"+str(modelIndex)].isdigit():
                                    requestDataInd['model'] = custom_params["model_"+str(modelIndex)]
                                    getData_genByModel.append(int(custom_params["model_"+str(modelIndex)]))
                                    if "gen_"+str(modelIndex) in custom_params:
                                        if custom_params["gen_"+str(modelIndex)] is not None and custom_params["gen_"+str(modelIndex)].isdigit():
                                            requestDataInd['gen'] = custom_params["gen_"+str(modelIndex)]

                            requestDataModel.append(requestDataInd)

                try:
                    get_mark = CarPropertyMark.objects.all().order_by("title")
                except:
                    get_mark = []

                for mark in get_mark:
                    getData['mark'].append({"id": mark.id, "name": mark.title, "object": mark})

                if len(getData_modelByMark) > 0:
                    try:
                        get_model = CarPropertyModel.objects.filter(mark_id__in=getData_modelByMark).order_by("title")
                    except:
                        get_model = {}
                    for model in get_model:
                        getData['model'].append({"id": model.id, "name": model.title, "mark": model.mark.id, "object": model})

                if len(getData_genByModel) > 0:
                    try:
                        get_gen = CarPropertyGen.objects.filter(model_id__in=getData_genByModel).order_by("title")
                    except:
                        get_gen = {}

                    for gen in get_gen:
                        getData['gen'].append({"id": gen.id, "name": gen.title, "model": gen.model.id, "object": gen})



                hasModelFilter = False
                for modelIndex in range(0, model_filter_count):
                    returnData = {"mark": [], "model": [], "gen": [], "is_active": False}
                    for mark in getData['mark']:
                        returnMark = {}
                        returnMark['id'] = mark['id']
                        returnMark['name'] = mark['name']
                        returnMark['is_active'] = False
                        returnMark['obj'] = mark
                        try:
                            checkDataIndex = requestDataModel[modelIndex]
                        except:
                            checkDataIndex = None
                        if checkDataIndex is not None:
                            if requestDataModel[modelIndex]['mark'] == str(returnMark['id']):
                                hasModelFilter = True
                                returnMark['is_active'] = True
                                returnData['is_active'] = True
                                for model in getData['model']:
                                    # print(str(model['mark'])+"___"+str(requestDataModel[modelIndex]['mark']))
                                    if int(model['mark']) == int(requestDataModel[modelIndex]['mark']):
                                        returnModel = {}
                                        returnModel['id'] = model['id']
                                        returnModel['mark_id'] = model['mark']
                                        returnModel['name'] = model['name']
                                        returnModel['is_active'] = False
                                        returnModel['obj'] = model
                                        if "model" in requestDataModel[modelIndex]:
                                            if requestDataModel[modelIndex]['model'] == str(returnModel['id']):
                                                returnModel['is_active'] = True
                                                for gen in getData['gen']:
                                                    if int(gen['model']) == int(requestDataModel[modelIndex]['model']):
                                                        returnGen = {}
                                                        returnGen['id'] = gen['id']
                                                        returnGen['name'] = gen['name']
                                                        returnGen['is_active'] = False
                                                        returnGen['obj'] = gen
                                                        if "gen" in requestDataModel[modelIndex]:
                                                            if requestDataModel[modelIndex]['gen'] == str(returnGen['id']):
                                                                returnGen['is_active'] = True
                                                        returnData['gen'].append(returnGen)
                                            returnData['model'].append(returnModel)
                        returnData['mark'].append(returnMark)
                    renderData['main_area']['model_filter'].append(returnData)

            if hasModelFilter is True:
                self.paramsForModel = []
                # self.paramsForFilter['mark_id__in'] = []
                # self.paramsForFilter['model_id__in'] = []
                # self.paramsForFilter['gen_id__in'] = []
                for model_filter in renderData['main_area']['model_filter']:
                    if model_filter['is_active'] is True:
                        paramItems = {'mark_id__in': [], "model_id__in": [], "gen_id__in": []}
                        for mark in model_filter['mark']:
                            if mark['is_active'] is True:
                                paramItems['mark_id__in'].append(mark['id'])
                        model_obj = None
                        for model in model_filter['model']:
                            if model['is_active'] is True:
                                paramItems['model_id__in'].append(model['id'])
                                model_obj = model['obj']
                        if model_obj is None:
                            for model in model_filter['model']:
                                paramItems['model_id__in'].append(model['id'])
                        if model_filter['gen'] is not None:
                            for gen in model_filter['gen']:
                                if gen['is_active'] is True:
                                    paramItems['gen_id__in'].append(gen['id'])

                        if not len(paramItems['gen_id__in']) > 0:
                            del paramItems['gen_id__in']
                        self.paramsForModel.append(paramItems)

            if main_area__property is True:
                renderData['main_area']['property'] = []
                # renderData['main_area']['property'].append(self.getFilterFields('engine', request, 'multi_select'))
                getFields = [
                    # "engine",
                    # "drive_type",
                ]

                nowDate = datetime.now()
                renderData['main_area']['property'].append(self.getFilterFieldsRange('year', request, 1890, nowDate.year, "select_range"))
                renderData['main_area']['property'].append(self.getFilterFields('engine', request, cf_to_ms=True))
                renderData['main_area']['property'].append(self.getFilterFields('drive_type', request, cf_to_ms=True))

                for fields in getFields:
                    get_field = self.getFilterFields(fields, request)
                    # renderData['main_area']['property'][fields] = None
                    if get_field is not None:
                        # renderData['main_area']['property'][fields] = get_field
                        renderData['main_area']['property'].append(get_field)

                renderData['main_area']['property'].append(self.getFilterFieldsRange('mileage', request, 0, 999999))
                renderData['main_area']['property'].append(self.getFilterFieldsRange('dvs', request, '0.1', '10', "select_range_dvs"))

                getFields = [
                    # "transmission",
                ]
                renderData['main_area']['property'].append(self.getFilterFields('transmission', request, cf_to_ms=True))

                for fields in getFields:
                    get_field = self.getFilterFields(fields, request)
                    # renderData['main_area']['property'][fields] = None
                    if get_field is not None:
                        # renderData['main_area']['property'][fields] = get_field
                        renderData['main_area']['property'].append(get_field)

                renderData['main_area']['property'].append(self.getFilterFields('body', request, 'multi_select'))
                renderData['main_area']['property'].append(self.getFilterFieldsRange('price', request, 0, 999999999))

                getFields = [
                    "has_photo",
                    "has_sell",
                    "has_guarantee",
                ]

                for fields in getFields:
                    get_field = self.getFilterFields(fields, request)
                    # renderData['main_area']['property'][fields] = None
                    if get_field is not None:
                        # renderData['main_area']['property'][fields] = get_field
                        renderData['main_area']['property'].append(get_field)


        if sub_area is True:
            renderData['sub_area'] = {"defend": None, "soft": None, "multi": None, "main": None}
            if sub_area__main is True:
                renderData['sub_area']['main'] = []
                renderData['sub_area']['main'].append(self.getFilterFields('color', request, 'color_select', subProp=True))
                renderData['sub_area']['main'].append(self.getFilterFieldsRange('horses_power', request, 0, 9999))
                getFields = [
                    # "engine",
                    # "dvs",
                    # "drive_type",
                    # "transmission",
                    "owner_count",
                    "pts",
                    "ownership",
                    "seat_count",
                    "door_count",
                    "has_pts"
                ]

                for fields in getFields:
                    get_field = self.getFilterFields(fields, request, subProp=True)
                    if get_field is not None:
                        renderData['sub_area']['main'].append(get_field)
            if sub_area__defend is True:
                renderData['sub_area']['defend'] = []
                getFields = [
                    # "airbag",
                    # "parktronic",
                    "sp_air",
                    "sp_park",
                    "cruise_control",
                    "headlights",
                    "power_steering",
                    # "security_system",
                    "sp_def",
                    "disk",
                    "disk_size",
                    "esp",
                    "abs",
                    "rain_sensor",
                    "lights_sensor",
                    "night_vision",
                    "hold_on_bar",
                    "monitor_dead_zone",
                    "ceramic_brakes",
                    "ISOFIX",
                    "autopilot",
                    "fog_lights",
                    "anti_slip_system"
                ]

                for fields in getFields:
                    get_field = self.getFilterFields(fields, request, subProp=True, cf_to_ms=True)
                    if get_field is not None:
                        renderData['sub_area']['defend'].append(get_field)
            if sub_area__soft is True:
                renderData['sub_area']['soft'] = []
                getFields = [
                    "luke",
                    "color_seat",
                    "color_roof",
                    "color_both",
                    "adjust_steering",
                    "climate",
                    "seat_adjust",
                    "seat_passenger_adjust",
                    "seat_back_passenger_adjust",
                    "seat_heating",
                    "seat_venting",
                    "seat",
                    "seat_massage",
                    "upholstary",
                    "interior_color",
                    "electric_window",
                    "colorInterior",
                    "multifunction_steering",
                    "heated_steering",
                    # "panorama_roof",
                    "power_mirror",
                    "electric_folding_mirror",
                    "mirror_heating",
                    "keyless_access",
                    "door_closer",
                    "electric_boot_drive",
                    "heated_windscreen",
                    "headlight_washer",
                    "preheater",
                    "air_suspension"
                ]

                for fields in getFields:
                    get_field = self.getFilterFields(fields, request, subProp=True, cf_to_ms=True)
                    if get_field is not None:
                        renderData['sub_area']['soft'].append(get_field)
            if sub_area__multi is True:
                renderData['sub_area']['multi'] = []
                getFields = [
                    "music",
                    # "music_os",
                    # "music_source",
                    "sp_os",
                    "sp_source",
                    "music_multimedia",
                    # "aux",
                    # "bluetooth",
                    # "usb",
                    "multimedia_rear_passengers",
                    "side_wind_projection",
                    "tv_tuner",
                    "navigation",
                    "dtb",
                    "w_charge",
                    "ethernet"
                ]

                for fields in getFields:
                    get_field = self.getFilterFields(fields, request, subProp=True, cf_to_ms=True)
                    if get_field is not None:
                        renderData['sub_area']['multi'].append(get_field)

                print(renderData['sub_area']['multi'])
            if sub_area__other is True:
                renderData['sub_area']['other'] = []
                getFields = [
                    "sport_package",
                    "m_package",
                    "s_package_out",
                    "s_package_in",
                    "amg_package",
                    "f_package",
                    "r_package",
                ]

                for fields in getFields:
                    get_field = self.getFilterFields(fields, request, subProp=True)
                    if get_field is not None:
                        renderData['sub_area']['other'].append(get_field)
        if save_search is True:
            renderData['save_search'] = True
        if renderData['main_area'] is not None:
            self.dateToParam(renderData['main_area']['property'])
        if renderData['sub_area'] is not None:
            self.dateToParam(renderData['sub_area']['multi'])
            self.dateToParam(renderData['sub_area']['other'])
            self.dateToParam(renderData['sub_area']['defend'])
            self.dateToParam(renderData['sub_area']['soft'])
        renderData['requestUrl'] = request.GET.urlencode()
        hasSaveFilter = False
        if len(self.paramsForFilter) > 0 or self.paramsForModel is not None or self.paramsForMulti is not None:
            hasSaveFilter = True
        renderData['hasSaveFilter'] = hasSaveFilter
        renderData['subPropCount'] = self.countSubProp

        template_path = "avtoportal/template/filter/filter.html"
        if filter_style == "default":
            template_path = "avtoportal/template_release/filter/filter.html"

        return render_to_string(template_path, renderData)

    def getFilterFields(self, name_fields, request, type=None, subProp=False, cf_to_ms=False):
        obj_car = Car()
        try:
            field = obj_car._meta.get_field(name_fields)
        except:
            field = None

        returnList = None
        if field is not None:
            returnList = {"title": field.verbose_name, "name_field": name_fields, "type": None, "values": [], "value": None}

            if field.get_internal_type() == "CharField" and cf_to_ms is True:
                returnList['type'] = 'multi_select_cf'
                returnList['value'] = []

                get_choices = field.choices
                for choices in get_choices:
                    body_item = {"id": choices[0], 'title': choices[1], 'is_active': False}

                    if name_fields in request.GET:
                        if str(choices[0]) in request.GET.getlist(name_fields):
                            if subProp is True:
                                self.countSubProp = int(self.countSubProp)+1
                            returnList['value'].append(choices[0])
                            body_item['is_active'] = True
                    returnList['values'].append(body_item)
            elif field.get_internal_type() == "CharField":
                if len(field.choices) > 0:
                    returnList['type'] = 'select'

                    returnList['values'].append({"id": 'show_all', 'title': 'Показать все', 'is_active': False})
                    get_choices = field.choices
                    for choices in get_choices:
                        seat_count_item = {"id": choices[0], 'title': choices[1], 'is_active': False}
                        if name_fields in request.GET:
                            if str(request.GET[name_fields]) == str(choices[0]):
                                if subProp is True:
                                    self.countSubProp = int(self.countSubProp)+1
                                seat_count_item['is_active'] = True
                                returnList['values'][0]['is_active'] = False
                                returnList['value'] = choices[0]
                        if name_fields in self.custom_params:
                            if str(self.custom_params[name_fields]) == str(choices[0]):
                                seat_count_item['is_active'] = True
                                returnList['values'][0]['is_active'] = False
                                returnList['value'] = choices[0]
                        returnList['values'].append(seat_count_item)

            elif field.get_internal_type() == "ForeignKey":
                if type == "multi_select":
                    returnList['type'] = 'multi_select'
                    returnList['value'] = []
                    returnList['groups'] = None
                    obj = field.rel.to

                    try:
                        get_from_obj = obj.objects.all()
                    except:
                        get_from_obj = []

                    for obj_element in get_from_obj:
                        body_item = {"id": obj_element.id, 'title': obj_element.title, 'is_active': False, 'main': None}
                        if name_fields == "body":
                            if returnList['groups'] is None:
                                returnList['groups'] = {}

                            if obj_element.group is not '':
                                body_item['main'] = obj_element.group
                            else:
                                body_item['main'] = "default"

                            if body_item['main'] in returnList['groups']:
                                returnList['groups'][body_item['main']]['values'].append(body_item)
                            else:
                                returnList['groups'][body_item['main']] = {'name': body_item['main'], 'values': []}
                                returnList['groups'][body_item['main']]['values'].append(body_item)

                        if name_fields in request.GET:
                            if str(obj_element.id) in request.GET.getlist(name_fields):
                                if subProp is True:
                                    self.countSubProp = int(self.countSubProp)+1
                                returnList['value'].append(obj_element.id)
                                body_item['is_active'] = True
                        # if name_fields in self.custom_params:
                        #     if str(obj_element.id) in self.custom_params.getlist(name_fields):
                        #         returnList['value'].append(obj_element.id)
                        #         body_item['is_active'] = True
                        returnList['values'].append(body_item)

                    returnList['values'] = sorted(returnList['values'], key=lambda k: k['main'])

                elif type == "color_select":
                    returnList['type'] = 'color_select'
                    returnList['value'] = []
                    obj = field.rel.to

                    try:
                        get_from_obj = obj.objects.all().order_by('sort_num')
                    except:
                        get_from_obj = []

                    for obj_element in get_from_obj:
                        body_item = {"id": obj_element.id, 'title': obj_element.title, "tag": obj_element.color_tag, 'is_active': False}
                        if name_fields in request.GET:
                            if str(obj_element.id) in request.GET.getlist(name_fields):
                                if subProp is True:
                                    self.countSubProp = int(self.countSubProp)+1
                                returnList['value'].append(obj_element.id)
                                body_item['is_active'] = True
                        # if name_fields in self.custom_params:
                        #     if str(obj_element.id) in self.custom_params.getlist(name_fields):
                        #         returnList['value'].append(obj_element.id)
                        #         body_item['is_active'] = True
                        returnList['values'].append(body_item)

            elif field.get_internal_type() == "ManyToManyField":
                if name_fields == 'colorInterior':
                    returnList['type'] = 'color_select'
                    returnList['value'] = []
                    obj = field.rel.to

                    try:
                        get_from_obj = obj.objects.all()
                    except:
                        get_from_obj = []

                    for obj_element in get_from_obj:
                        body_item = {"id": obj_element.id, 'title': obj_element.title, "tag": obj_element.color_tag, 'is_active': False}
                        if name_fields in request.GET:
                            if str(obj_element.id) in request.GET.getlist(name_fields):
                                if subProp is True:
                                    self.countSubProp = int(self.countSubProp)+1
                                returnList['value'].append(obj_element.id)
                                body_item['is_active'] = True
                        returnList['values'].append(body_item)
                else:
                    returnList['type'] = 'multi_select'
                    returnList['value'] = []
                    obj = field.rel.to

                    try:
                        get_from_obj = obj.objects.all()
                    except:
                        get_from_obj = []

                    for obj_element in get_from_obj:
                        body_item = {"id": obj_element.id, 'title': obj_element.title, 'is_active': False}
                        if name_fields == "body":
                            body_item['main'] = obj_element.main_body.id
                        if name_fields in request.GET:
                            if str(obj_element.id) in request.GET.getlist(name_fields):
                                if subProp is True:
                                    self.countSubProp = int(self.countSubProp)+1
                                returnList['value'].append(obj_element.id)
                                body_item['is_active'] = True
                        returnList['values'].append(body_item)


            elif field.get_internal_type() == "BooleanField":
                returnList['type'] = 'checkbox'
                returnList['values'] = {}
                returnList['values'] = {"value": True, 'is_active': False}
                if name_fields in request.GET:
                    if request.GET[name_fields] == "True":
                        if subProp is True:
                            self.countSubProp = int(self.countSubProp)+1
                        returnList['values']['is_active'] = True
                        returnList['value'] = True
        return returnList

    def getFilterFieldsInput(self, name_fields, request):
        obj_car = Car()
        try:
            field = obj_car._meta.get_field(name_fields)
        except:
            field = None

        returnList = None
        if field is not None:
            returnList = {"title": field.verbose_name, "name_field": name_fields, "type": "input",
                          "value": ""}
            if name_fields in request.GET:
                returnList['value'] = request.GET[name_fields]

        return returnList

    def getFilterFieldsRange(self, name_fields, request, min, max, type="input_range", decimal=False):
        obj_car = Car()
        try:
            field = obj_car._meta.get_field(name_fields)
        except:
            field = None

        returnList = None
        if field is not None:
            if type == "input_range":
                returnList = {"title": field.verbose_name, "name_field": name_fields, "type": "input_range", "value_min": "", "value_max": "", "min": min, "max": max}

                if name_fields+"_min" in request.GET:
                    if request.GET[name_fields+"_min"].isdigit():
                        returnList['value_min'] = int(request.GET[name_fields+"_min"])
                if name_fields+"_max" in request.GET:
                    if request.GET[name_fields+"_max"].isdigit():
                        returnList['value_max'] = int(request.GET[name_fields+"_max"])
                if name_fields+"_min" in self.custom_params:
                    if self.custom_params[name_fields+"_min"].isdigit():
                        returnList['value_min'] = int(self.custom_params[name_fields+"_min"])
                if name_fields+"_max" in self.custom_params:
                    if self.custom_params[name_fields+"_max"].isdigit():
                        returnList['value_max'] = int(self.custom_params[name_fields+"_max"])
            elif type == "select_range":
                returnList = {"title": field.verbose_name, "name_field": name_fields, "type": "select_range", "value_min": None, "value_max": None, "values_min": [], "values_max": [], "min": min, "max": max}

                getChoice = self.__getRangeForChoice(min, max)
                returnList['values_min'].append({"value": "Все", 'is_active': False, "is_default": True})
                returnList['values_max'].append({"value": "Все", 'is_active': False, "is_default": True})
                for choice in getChoice:
                    choice_min = {"value": choice, 'is_active': False}
                    choice_max = {"value": choice, 'is_active': False}

                    if name_fields+"_min" in request.GET:
                        if request.GET[name_fields+"_min"] == str(choice):
                            returnList['value_min'] = choice
                            returnList['values_min'][0]['is_active'] = False
                            choice_min['is_active'] = True
                    if name_fields+"_max" in request.GET:
                        if request.GET[name_fields+"_max"] == str(choice):
                            returnList['value_max'] = choice
                            returnList['values_max'][0]['is_active'] = False
                            choice_max['is_active'] = True
                    if name_fields+"_min" in self.custom_params:
                        if self.custom_params[name_fields+"_min"] == str(choice):
                            returnList['value_min'] = choice
                            returnList['values_min'][0]['is_active'] = False
                            choice_min['is_active'] = True
                    if name_fields+"_max" in self.custom_params:
                        if self.custom_params[name_fields+"_max"] == str(choice):
                            returnList['value_max'] = choice
                            returnList['values_max'][0]['is_active'] = False
                            choice_max['is_active'] = True

                    returnList['values_min'].append(choice_min)
                    returnList['values_max'].append(choice_max)

                returnList['values_min'] = list(reversed(returnList['values_min']))
                returnList['values_max'] = list(reversed(returnList['values_max']))
                # returnList['values_min'] = returnList['values_min']
                # returnList['values_max'] = returnList['values_max']
            elif type == "select_range_dvs":
                returnList = {"title": field.verbose_name, "name_field": name_fields, "type": "select_range_dvs", "value_min": None, "value_max": None, "values_min": [], "values_max": [], "min": min, "max": max}

                getChoice = self.__getRangeForChoiceDecimal()
                returnList['values_min'].append({"value": "Все", 'is_active': False, "is_default": True})
                returnList['values_max'].append({"value": "Все", 'is_active': False, "is_default": True})
                for choice in getChoice:
                    choice_min = {"id": choice['id'], "value": choice['title'], 'is_active': False}
                    choice_max = {"id": choice['id'], "value": choice['title'], 'is_active': False}

                    if name_fields+"_min" in request.GET:
                        if request.GET[name_fields+"_min"] == str(choice['id']):
                            returnList['value_min'] = choice['id']
                            returnList['values_min'][0]['is_active'] = False
                            choice_min['is_active'] = True
                    if name_fields+"_max" in request.GET:
                        if request.GET[name_fields+"_max"] == str(choice['id']):
                            returnList['value_max'] = choice['id']
                            returnList['values_max'][0]['is_active'] = False
                            choice_max['is_active'] = True
                    if name_fields+"_min" in self.custom_params:
                        if self.custom_params[name_fields+"_min"] == str(choice['id']):
                            returnList['value_min'] = choice['id']
                            returnList['values_min'][0]['is_active'] = False
                            choice_min['is_active'] = True
                    if name_fields+"_max" in self.custom_params:
                        if self.custom_params[name_fields+"_max"] == str(choice['id']):
                            returnList['value_max'] = choice['id']
                            returnList['values_max'][0]['is_active'] = False
                            choice_max['is_active'] = True

                    returnList['values_min'].append(choice_min)
                    returnList['values_max'].append(choice_max)

                # returnList['values_min'] = reversed(returnList['values_min'])
                # returnList['values_max'] = reversed(returnList['values_max'])


        return returnList

    def __getRangeForChoiceDecimal(self):
        result = []
        for ind, num in enumerate(range(1, 101)):
            formatNum = "{:3.1f}".format((float(num)*0.1))
            elementResult = {"id": str(ind), "title": float(formatNum)}
            result.append(elementResult)
        return result

    def __getRangeForChoice(self, min, max):
        result = []
        max = int(max)+1
        for ind, num in enumerate(range(min, max)):
            result.append(num)
        return result

    def dateToParam(self, data):
        if data is not None:
            for prop in data:
                if prop['type'] == "select":
                    if prop['value'] is not None:
                        self.paramsForFilter[prop['name_field']] = prop['value']
                if prop['type'] == "input":
                    if prop['value']:
                        if prop['name_field'] == 'vin':
                            self.paramsForFilter[prop['name_field']] = prop['value'].lower()
                        else:
                            self.paramsForFilter[prop['name_field']] = prop['value']
                if prop['type'] == "color_select":
                    if len(prop['value']) > 0:
                        if prop['name_field'] != "color":
                            if self.paramsForMulti is None:
                                self.paramsForMulti = {}
                            self.paramsForMulti[prop['name_field']+"__id__in"] = prop['value']
                        else:
                            self.paramsForFilter[str(prop['name_field']) + "_id__in"] = prop['value']
                if prop['type'] == "multi_select":
                    if len(prop['value']) > 0:
                        if prop['name_field'] != "body":
                            if self.paramsForMulti is None:
                                self.paramsForMulti = {}
                            self.paramsForMulti[prop['name_field']+"__id__in"] = prop['value']
                        else:
                            self.paramsForFilter[str(prop['name_field']) + "_id__in"] = prop['value']
                if prop['type'] == "multi_select_cf":
                    if len(prop['value']) > 0:
                        self.paramsForFilter[str(prop['name_field']) + "__in"] = prop['value']
                if prop['type'] == "select_range_dvs":
                    if prop['value_min'] is not None or prop['value_max'] is not None:
                        get_dvs = self.__getRangeForChoiceDecimal()
                        dvs_range = []
                        for dvs in get_dvs:
                            if prop['value_min'] is None and prop['value_max'] is not None:
                                if int(dvs['id']) <= int(prop['value_max']):
                                    dvs_range.append(dvs['id'])
                            elif prop['value_min'] is not None and prop['value_max'] is None:
                                if int(dvs['id']) >= int(prop['value_min']):
                                    dvs_range.append(dvs['id'])
                            else:
                                if int(dvs['id']) >= int(prop['value_min']) and int(dvs['id']) <= int(prop['value_max']):
                                    dvs_range.append(dvs['id'])
                        self.paramsForFilter[str(prop['name_field'])+"__in"] = dvs_range
                if prop['type'] == "select_range":
                    if prop['value_min'] is not None or prop['value_max'] is not None:
                        if prop['value_min'] is not None:
                            range_min = prop['value_min']
                        else:
                            range_min = prop['min']
                        if prop['value_max'] is not None:
                            range_max = prop['value_max']
                        else:
                            range_max = prop['max']

                        self.paramsForFilter[str(prop['name_field'])+"__range"] = (range_min, range_max)
                if prop['type'] == "input_range":
                    if prop['value_min'] != "" or prop['value_max'] != "":
                        if prop['value_min'] != "":
                            range_min = prop['value_min']
                        else:
                            range_min = prop['min']
                        if prop['value_max'] != "":
                            range_max = prop['value_max']
                        else:
                            range_max = prop['max']

                        self.paramsForFilter[str(prop['name_field'])+"__range"] = (range_min, range_max)
                if prop['type'] == "checkbox":
                    if prop['value'] is True:
                        self.paramsForFilter[prop['name_field']] = prop['value']
    def save_filter(self, request, filter_name, other_params=None, for_path="/catalog/", is_user_car=False):
        returnData = {"success": False, "error_mes": None, "filter": None}
        if self.paramsForFilter is not None and request.user.is_authenticated():
            if filter_name is not None:
                if len(filter_name) <= 100:
                    paramsUrl = None
                    allParams = self.paramsForFilter

                    if other_params is not None:
                        self.paramsForFilter.update(other_params)
                    paramsJSON = json.dumps(self.paramsForFilter)
                    paramsModelJSON = None
                    paramsMultiJSON = None
                    if 'color_id__in' in allParams:
                        allParams['color'] = allParams['color_id__in']
                        del allParams['color_id__in']
                    if 'body_id__in' in allParams:
                        allParams['body'] = allParams['body_id__in']
                        del allParams['body_id__in']
                    if 'mileage__range' in allParams:
                        allParams['mileage_min'] = allParams['mileage__range'][0]
                        allParams['mileage_max'] = allParams['mileage__range'][1]
                        del allParams['mileage__range']
                    if 'price__range' in allParams:
                        allParams['price_min'] = allParams['price__range'][0]
                        allParams['price_max'] = allParams['price__range'][1]
                        del allParams['price__range']
                    if 'year__range' in allParams:
                        allParams['year_min'] = allParams['year__range'][0]
                        allParams['year_max'] = allParams['year__range'][1]
                        del allParams['year__range']
                    if 'dvs__in' in allParams:
                        allParams['dvs_min'] = allParams['dvs__in'][0]
                        allParams['dvs_max'] = allParams['dvs__in'][-1]
                        del allParams['dvs__in']
                    if 'author__profile__from_city_id__in' in allParams:
                        allParams['search_city'] = allParams['author__profile__from_city_id__in']
                        del allParams['author__profile__from_city_id__in']
                    if self.paramsForModel is not None:
                        # mark_id__in': [87], 'gen_id__in': [1306], 'model_id__in': [543]
                        for ind, param in enumerate(self.paramsForModel):
                            if param['mark_id__in'] is not None and len(param['mark_id__in']) == 1:
                                allParams['mark_'+str(ind)] = param['mark_id__in'][0]
                            if 'model_id__in' in param:
                                if param['model_id__in'] is not None and len(param['model_id__in']) == 1:
                                    allParams['model_'+str(ind)] = param['model_id__in'][0]
                            if 'gen_id__in' in param:
                                if param['gen_id__in'] is not None and len(param['gen_id__in']) == 1:
                                    allParams['gen_'+str(ind)] = param['gen_id__in'][0]
                            paramsModelJSON = json.dumps(self.paramsForModel)
                    if self.paramsForMulti is not None:
                        if "colorInterior__id__in" in self.paramsForMulti:
                            allParams.update({'colorInterior': self.paramsForMulti["colorInterior__id__in"]})
                        if "paint_element__id__in" in self.paramsForMulti:
                            allParams.update({'paint_element': self.paramsForMulti["paint_element__id__in"]})
                        paramsMultiJSON = json.dumps(self.paramsForMulti)

                    paramsUrl = urllib.parse.urlencode(allParams, doseq=True)
                    paramsUrl = "%s?%s" % (for_path, paramsUrl)

                    try:
                        get_filter = SaveFilter.objects.get(jsonStringForModel=paramsModelJSON,
                                                            jsonStringForMulti=paramsMultiJSON,
                                                            jsonStringForParams=paramsJSON)
                    except:
                        get_filter = None

                    if get_filter is None:
                        get_filter = SaveFilter.objects.create(jsonStringForModel=paramsModelJSON,
                                                    jsonStringForMulti=paramsMultiJSON,
                                                    jsonStringForParams=paramsJSON,
                                                    url=paramsUrl)
                        get_filter.save()

                    if is_user_car is False:
                        try:
                            get_user_filter = UserSaveFilter.objects.get(user_id=request.user.id, filter_id=get_filter.id)
                        except:
                            get_user_filter = None

                        if get_user_filter is None:
                            user_filter = UserSaveFilter.objects.create(user=request.user,
                                                                        filter=get_filter,
                                                                        name=filter_name)
                            user_filter.save()
                            returnData['success'] = True

                        else:
                            returnData['error_mes'] = {"title": "Такой фильтр уже существует",
                                                       "mess": "Фильтр с такими параметрами уже существет под именем \""+str(get_user_filter.name)+"\""}
                    else:
                        returnData['success'] = True
                        returnData['filter'] = get_filter
                else:
                    returnData['error_mes'] = {"title": "Имя фильтра не коректно",
                                               "mess": "Имя фильтра должно быть не более 100 символов"}
            else:
                returnData['error_mes'] = {"title": "Имя фильтра не введено",
                                           "mess": "Имя фильтра должно быть указано"}
        else:
            returnData['error_mes'] = {"title": "Нужно авторизироватся",
                                       "mess": "Сохранять фильтр могут только авторизированные пользователи"}
        return returnData

class RenderPageNavigation():
    def renderHTML(self, request, endPage, startPage=1, selectPage=1, paramUrl="page", dopParam=None):

        # requestGetList = self.requestGetToDict(request)
        requestUrl = request.GET.urlencode()

        dataForRender = []
        for pageIndex in range(startPage, (int(endPage)+1)):
            pageNavItem = {}
            pageNavItem['title'] = str(pageIndex)
            pageNavItem['select'] = False
            if int(pageIndex) == int(selectPage):
                pageNavItem['select'] = True
            # requestGetList[paramUrl] = str(pageIndex)
            # params = urllib.parse.urlencode(requestGetList)
            pageNavItem['url'] = "?%s&%s=%s" % (requestUrl, paramUrl, str(pageIndex))
            if dopParam is not None:
                for ind, dopParamItem in dopParam.items():
                    pageNavItem['url'] = "%s&%s=%s" % (pageNavItem['url'], ind, dopParamItem)

            dataForRender.append(pageNavItem)

        return render_to_string('avtoportal/template/page_navigation/catalog.html', {"dataForRender": dataForRender})

    def requestGetToDict(self, request):
        requestGetList = {}
        for ing, getItem in request.GET.items():
            if request.GET.getlist(ing):
                requestGetList[ing] = request.GET.getlist(ing)

        return requestGetList

def getMainParamsForCar(car):
    returnData = None
    fields = [
        "year",
        # "year_reg",
        # "date_reg",
        "mileage",
        "horses_power",
        "body",
    ]
    fields_select = [
        "engine",
        "dvs",
        "drive_type",
        "gear_count",
        "pts",
        "owner_count",
        # "state",
        "door_count",
        "color_dop",
        "new_or_use",
        "ownership",
        "transmission",
    ]
    if car is not None:
        returnData = []
        for defend_item in fields_select:
            try:
                field = car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                field_value = getattr(car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if field_value:
                    field_value = getattr(car, "get_" + str(defend_item) + "_display")
                    fieldData['value'] = field_value
                else:
                    fieldData['value'] = "Не указано"
                returnData.append(fieldData)
        for defend_item in fields:
            try:
                field = car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                field_value = getattr(car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                fieldData['value'] = field_value
                if not field_value:
                    fieldData['value'] = "Не указано"
                returnData.append(fieldData)

        color = car.color
        fieldData = {}
        if color is not None:
            fieldData['title'] = "Цвет"
            fieldData['value'] = color.title
            fieldData['tag'] = color.color_tag
            returnData.append(fieldData)

        paint_element_list = car.paint_element.all()
        fieldData = {}
        fieldData['title'] = "Крашеные элементы"
        fieldData['code'] = "paint_element"
        fieldData['value'] = []
        for paint_element_item in paint_element_list:
            fieldData['value'].append({"title": paint_element_item.title})
        if len(fieldData['value']) > 0:
            returnData.append(fieldData)
    return returnData
def getDopForCar(car_id):

    returnData = {"defend": None, "soft": None, "multi": None, "other": None, "colorInterior": None}

    try:
        get_car = Car.objects.get(id=car_id)
    except:
        get_car = None

    DEFEND = [
        "airbag",
        "parktronic",
        "cruise_control",
        "headlights",
        "power_steering",
        "security_system",
        "disk",
        "disk_size",
    ]
    DEFEND_CHECK_BOX = [
        "esp",
        "abs",
        "rain_sensor",
        "lights_sensor",
        "night_vision",
        "hold_on_bar",
        "monitor_dead_zone",
        "ceramic_brakes",
        "ISOFIX",
        "autopilot",
        "fog_lights",
        "anti_slip_system"
    ]

    SOFT = [
                    "luke",
                    "color_seat",
                    "color_roof",
                    "color_both",
                    "adjust_steering",
                    "climate",
                    "seat_adjust",
                    "seat_passenger_adjust",
                    "seat_back_passenger_adjust",
                    "seat_heating",
                    "seat_venting",
                    "seat",
                    "seat_massage",
                    "upholstary",
                    "interior_color",
                    "electric_window",
                    # "colorInterior",
                    # "panorama_roof",
    ]
    SOFT_CHECK_BOX = [
                    "heated_steering",
                    "power_mirror",
                    "multifunction_steering",
                    "electric_folding_mirror",
                    "mirror_heating",
                    "keyless_access",
                    "door_closer",
                    "electric_boot_drive",
                    "heated_windscreen",
                    "headlight_washer",
                    "preheater",
                    "air_suspension"
    ]

    MULTI = [
                    "music",
                    "music_os",
                    "music_source",
                    "music_multimedia",
                    # "aux",
                    # "bluetooth",
                    # "usb",
    ]
    MULTI_CHECK_BOX = [
        "multimedia_rear_passengers",
        "side_wind_projection",
        "tv_tuner",
        "navigation",
        "dtb",
        "w_charge",
        "ethernet"
    ]

    OTHER = [
        "sport_package",
        "m_package",
        "s_package_out",
        "s_package_in",
        "amg_package",
        "f_package",
        "r_package",
    ]

    if get_car is not None:
        returnData['defend'] = []
        for defend_item in DEFEND:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                # field_value = getattr(get_car, "get_"+str(defend_item)+"_display")
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if field_value:
                    field_value = getattr(get_car, "get_" + str(defend_item) + "_display")
                    fieldData['value'] = field_value
                else:
                    fieldData['value'] = "Не указано"
                    continue
                returnData['defend'].append(fieldData)
        returnData['defend_check'] = []
        for defend_item in DEFEND_CHECK_BOX:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if field_value is False:
                    fieldData['value'] = "Нет"
                else:
                    fieldData['value'] = "Да"
                    returnData['defend_check'].append(fieldData)
        returnData['soft'] = []
        for defend_item in SOFT:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if not field_value:
                    fieldData['value'] = "Не указано"
                    continue
                else:
                    field_value = getattr(get_car, "get_" + str(defend_item) + "_display")
                    fieldData['value'] = field_value
                returnData['soft'].append(fieldData)
        returnData['soft_check'] = []
        for defend_item in SOFT_CHECK_BOX:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if field_value is False:
                    fieldData['value'] = "Нет"
                else:
                    fieldData['value'] = "Да"
                    returnData['soft_check'].append(fieldData)
        returnData['colorInterior'] = []
        colorInterior_list = get_car.colorInterior.all()
        for colorInterior_item in colorInterior_list:
            returnData['colorInterior'].append({"title": colorInterior_item.title,
                                                "code": "colorInterior",
                                                "tag": colorInterior_item.color_tag})
        returnData['multi'] = []
        for defend_item in MULTI:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                # field_value = getattr(get_car, "get_"+str(defend_item)+"_display")
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if not field_value:
                    fieldData['value'] = "Не указано"
                    continue
                else:
                    field_value = getattr(get_car, "get_" + str(defend_item) + "_display")
                    fieldData['value'] = field_value
                returnData['multi'].append(fieldData)
        returnData['multi_check'] = []
        for defend_item in MULTI_CHECK_BOX:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if field_value is False:
                    fieldData['value'] = "Нет"
                else:
                    fieldData['value'] = "Да"
                    returnData['multi_check'].append(fieldData)
        returnData['other'] = []
        for defend_item in OTHER:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if field_value is False:
                    fieldData['value'] = "Нет"
                else:
                    fieldData['value'] = "Да"
                    returnData['other'].append(fieldData)
    return returnData
def getDopForCarCompare(car_id):

    returnData = {"defend": None, "soft": None, "multi": None, "other": None, "colorInterior": None}

    try:
        get_car = Car.objects.get(id=car_id)
    except:
        get_car = None

    DEFEND = [
        "airbag",
        "parktronic",
        "cruise_control",
        "headlights",
        "power_steering",
        "security_system",
        "disk",
        "disk_size",
    ]
    DEFEND_CHECK_BOX = [
        "esp",
        "abs",
        "rain_sensor",
        "lights_sensor",
        "night_vision",
        "hold_on_bar",
        "monitor_dead_zone",
        "ceramic_brakes",
        "ISOFIX",
        "autopilot",
        "fog_lights",
        "anti_slip_system"
    ]

    SOFT = [
                    "luke",
                    "color_seat",
                    "color_roof",
                    "color_both",
                    "adjust_steering",
                    "climate",
                    "seat_adjust",
                    "seat_passenger_adjust",
                    "seat_back_passenger_adjust",
                    "seat_heating",
                    "seat_venting",
                    "seat",
                    "seat_massage",
                    "upholstary",
                    "interior_color",
                    "electric_window",
                    # "colorInterior",
                    # "panorama_roof",
    ]
    SOFT_CHECK_BOX = [
                    "heated_steering",
                    "power_mirror",
                    "multifunction_steering",
                    "electric_folding_mirror",
                    "mirror_heating",
                    "keyless_access",
                    "door_closer",
                    "electric_boot_drive",
                    "heated_windscreen",
                    "headlight_washer",
                    "preheater",
                    "air_suspension"
    ]

    MULTI = [
                    "music",
                    "music_os",
                    "music_source",
                    "music_multimedia",
                    # "aux",
                    # "bluetooth",
                    # "usb",
    ]
    MULTI_CHECK_BOX = [
        "multimedia_rear_passengers",
        "side_wind_projection",
        "tv_tuner",
        "navigation",
        "dtb",
        "w_charge",
        "ethernet"
    ]

    OTHER = [
        "sport_package",
        "m_package",
        "s_package_out",
        "s_package_in",
        "amg_package",
        "f_package",
        "r_package",
    ]

    if get_car is not None:
        returnData['defend'] = []
        for defend_item in DEFEND:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                # field_value = getattr(get_car, "get_"+str(defend_item)+"_display")
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if field_value:
                    field_value = getattr(get_car, "get_" + str(defend_item) + "_display")
                    fieldData['value'] = field_value
                else:
                    fieldData['value'] = "Не указано"
                returnData['defend'].append(fieldData)
        returnData['defend_check'] = []
        for defend_item in DEFEND_CHECK_BOX:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if field_value is False:
                    fieldData['value'] = "Нет"
                else:
                    fieldData['value'] = "Да"
                returnData['defend_check'].append(fieldData)
        returnData['soft'] = []
        for defend_item in SOFT:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if not field_value:
                    fieldData['value'] = "Не указано"
                else:
                    field_value = getattr(get_car, "get_" + str(defend_item) + "_display")
                    fieldData['value'] = field_value
                returnData['soft'].append(fieldData)
        returnData['soft_check'] = []
        for defend_item in SOFT_CHECK_BOX:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if field_value is False:
                    fieldData['value'] = "Нет"
                else:
                    fieldData['value'] = "Да"
                returnData['soft_check'].append(fieldData)
        returnData['colorInterior'] = []
        colorInterior_list = get_car.colorInterior.all()
        for colorInterior_item in colorInterior_list:
            returnData['colorInterior'].append({"title": colorInterior_item.title,
                                                "code": "colorInterior",
                                                "tag": colorInterior_item.color_tag})
        returnData['multi'] = []
        for defend_item in MULTI:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                # field_value = getattr(get_car, "get_"+str(defend_item)+"_display")
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if not field_value:
                    fieldData['value'] = "Не указано"
                else:
                    field_value = getattr(get_car, "get_" + str(defend_item) + "_display")
                    fieldData['value'] = field_value
                returnData['multi'].append(fieldData)
        returnData['multi_check'] = []
        for defend_item in MULTI_CHECK_BOX:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if field_value is False:
                    fieldData['value'] = "Нет"
                else:
                    fieldData['value'] = "Да"
                returnData['multi_check'].append(fieldData)
        returnData['other'] = []
        for defend_item in OTHER:
            try:
                field = get_car._meta.get_field(defend_item)
            except:
                field = None

            if field is not None:
                field_value = getattr(get_car, str(defend_item))
                fieldData = {}
                fieldData['title'] = field.verbose_name
                if field_value is False:
                    fieldData['value'] = "Нет"
                else:
                    fieldData['value'] = "Да"
                returnData['other'].append(fieldData)
    return returnData