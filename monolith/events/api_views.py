from django.http import JsonResponse
from .models import Conference, Location
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
import json
from events.models import State
from .acls import get_weather_data, get_photo


class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "state",
        "picture_url",
    ]

    def get_extra_data(self, o):
        return {"state": o.state.abbreviation}


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name"]


class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location"
    ]
    encoders = {
        "location": LocationListEncoder(),
    }


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
    ]


@require_http_methods(["GET", "POST"])
def api_list_conferences(request):
    """
    Lists the conference names and the link to the conference.

    Returns a dictionary with a single key "conferences" which
    is a list of conference names and URLS. Each entry in the list
    is a dictionary that contains the name of the conference and
    the link to the conference's information.

    {
        "conferences": [
            {
                "name": conference's name,
                "href": URL to the conference,
            },
            ...
        ]
    }
    """
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse({
             "conferences": conferences},
             encoder=ConferenceListEncoder,
        )
    else:
        content = json.loads(request.body)
        try:
            location = Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid location id"},
                status=400,
            )
        conference = Conference.objects.create(**content)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False
        )


@require_http_methods(["GET", "PUT", "DELETE"])
def api_show_conference(request, pk):
    """
    Returns the details for the Conference model specified
    by the pk parameter.

    This should return a dictionary with the name, starts,
    ends, description, created, updated, max_presentations,
    max_attendees, and a dictionary for the location containing
    its name and href.

    {
        "weather": {
    "temp": temperature in Fahrenheit (imperial measure),
    "description": the description of the weather, like "overcast clouds"
      },

        "name": the conference's name,
        "starts": the date/time when the conference starts,
        "ends": the date/time when the conference ends,
        "description": the description of the conference,
        "created": the date/time when the record was created,
        "updated": the date/time when the record was updated,
        "max_presentations": the maximum number of presentations,
        "max_attendees": the maximum number of attendees,
        "location": {
            "name": the name of the location,
            "href": the URL for the location,
        }
    }
    """
    # The first parameter, data, should be a dict instance. If the safe parameter is set to False (see below) it can be any JSON-serializable object.
    if request.method == "GET":
        conference = Conference.objects.get(id=pk)
        city = conference.location.city
        state = conference.location.state.abbreviation
        weather = get_weather_data(city, state)
        return JsonResponse(
               {"conference": conference, "weather": weather},
               encoder=ConferenceDetailEncoder,

         )
    elif request.method == "PUT":
        content = json.loads(request.body)
        try:
            if "location" in content:
                location = Location.objects.get(id=content["location"])
                content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid location id"},
                status=400,
            )
        Conference.objects.filter(id=pk).update(**content)
        conference = Conference.objects.get(id=pk)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False
        )

    else:
        count, _ = Conference.objects.get(id=pk).delete()
        return JsonResponse(
                {"delete": count > 0},
        )


@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    """
    Lists the location names and the link to the location.

    Returns a dictionary with a single key "locations" which
    is a list of location names and URLS. Each entry in the list
    is a dictionary that contains the name of the location and
    the link to the location's information.

    {
        "locations": [
            {
                "name": location's name,
                "href": URL to the location,
            },
            ...
        ]
    }
    """
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse({
                  "locations": locations},
                  encoder=LocationListEncoder)
    else:
        content = json.loads(request.body)
        try:
            # Get the State object and put it in the content dict
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state

        except State.DoesNotExist:
            return JsonResponse(
                                {"message": "Invalid state abbreviation"},
                                status=400,)
        picture_url = get_photo(content["city"], content["state"].abbreviation)
        content.update(picture_url)

        location = Location.objects.create(**content)
        return JsonResponse(
                       location,
                       encoder=LocationDetailEncoder,
                       safe=False
        )


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, pk):
    """
    Returns the details for the Location model specified
    by the pk parameter.

    This should return a dictionary with the name, city,
    room count, created, updated, and state abbreviation.

    {
        "name": location's name,
        "city": location's city,
        "room_count": the number of rooms available,
        "created": the date/time when the record was created,
        "updated": the date/time when the record was updated,
        "state": the two-letter abbreviation for the state,
    }
    """
    if request.method == "GET":
        location = Location.objects.get(id=pk)
        return JsonResponse(
                 location,
                 encoder=LocationDetailEncoder,
                 safe=False
         )
    elif request.method == "PUT":
        content = json.loads(request.body)
        try:
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                 {"message": "Invalid state abbreviation"},
                 status=400,
              )
        # here we need to add the photo variable to our model and Encoder too and migrate
        photo = get_photo(content["city"], content["state"].abbreviation)
        content.update(photo)

        Location.objects.filter(id=pk).update(**content)
        location = Location.objects.get(id=pk)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False
        )
    else:
        count, _ = Location.objects.filter(id=pk).delete()
        return JsonResponse({"deleted:": count > 0})
