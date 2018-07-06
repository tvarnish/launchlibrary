from collections import namedtuple
import requests

class LaunchLibrary():
    # Define named tuples for API objects
    __LaunchEvent = namedtuple("LaunchEvent",
                               "id name videos window status rocket location "
                               "missions lsp")

    __LaunchWindow = namedtuple("LaunchWindow",
                                "start end net isostart isoend isonet")

    __LaunchStatus = namedtuple("LaunchStatus",
                                "holdreason failreason changed "
                                "inhold name description")

    __LaunchStatusCode = namedtuple("LaunchStatusCode",
                                    "name description")

    __Rocket = namedtuple("Rocket",
                          "id name configuration familyname imageURL "
                          "wikiURL agencies")

    __Agency = namedtuple("Agency", "id name abbreviation countrycode wikiURL")

    __LaunchLocation = namedtuple("LaunchLocation", "id name countrycode pads")

    __LaunchPad = namedtuple("LaunchPad", "id name latitude longitude")

    __Mission = namedtuple("Mission",
                           "id name description type typeName "
                           "wikiURL agencies")

    __LSP = namedtuple("LSP", "id name abbreviation countrycode wikiURL")

    def __init__(self, version=1.4):
        self.__API_ROOT = "https://launchlibrary.net/" + str(version) + "/"

    def __APICall(self, endpoint):
        response = requests.get(self.__API_ROOT + endpoint)
        return response.json()

    # API JSON Object Parsing
    def __ParseObject(self, objectJSON, keys):
        data = []
        for key in keys:
            try:
                data.append(objectJSON[key])
            except KeyError:
                data.append(None)
        return data

    def __ParseLaunchWindow(self, launchJSON):
        windowKeys = ['windowstart',
                      'windowend',
                      'net',
                      'isostart',
                      'isoend',
                      'isonet']
        window = self.__LaunchWindow(*self.__ParseObject(launchJSON,
                                                         windowKeys))
        return window

    def __ParseLaunchStatusCode(self, launchStatusCode):
        response = self.__APICall("launchstatus/" + str(launchStatusCode))
        codeJSON = response['types'][0]

        codeKeys = ['name',
                    'description']
        statusCode = self.__LaunchStatusCode(*self.__ParseObject(codeJSON,
                                                                 codeKeys))
        return statusCode.name, statusCode.description

    def __ParseLaunchStatus(self, launchJSON):
        statusKeys = ['holdreason',
                      'failreason',
                      'changed',
                      'inhold']
        name, desc = self.__ParseLaunchStatusCode(launchJSON['status'])
        status = self.__LaunchStatus(*self.__ParseObject(launchJSON,
                                                         statusKeys),
                                     name, desc)
        return status

    def __ParseAgency(self, agencyJSON):
        agencyKeys = ['id',
                      'name',
                      'abbrev',
                      'countryCode',
                      'wikiURL']
        agency = self.__Agency(*self.__ParseObject(agencyJSON, agencyKeys))
        return agency

    def __ParseRocket(self, rocketJSON):
        rocketKeys = ['id',
                      'name',
                      'configuration',
                      'familyname',
                      'imageURL',
                      'wikiURL']

        rocketAgencies = []
        for agencyJSON in rocketJSON['agencies']:
            agency = self.__ParseAgency(agencyJSON)
            rocketAgencies.append(agency)

        rocket = self.__Rocket(*self.__ParseObject(rocketJSON, rocketKeys),
                               rocketAgencies)
        return rocket

    def __ParsePad(self, padJSON):
        padKeys = ['id',
                   'name',
                   'latitude',
                   'longitude']
        pad = self.__LaunchPad(*self.__ParseObject(padJSON, padKeys))
        return pad

    def __ParseLocation(self, locationJSON):
        pads = []
        for padJSON in locationJSON['pads']:
            pad = self.__ParsePad(padJSON)
            pads.append(pad)

        locationKeys = ['id',
                        'name',
                        'countryCode']
        location = self.__LaunchLocation(*self.__ParseObject(locationJSON,
                                                             locationKeys),
                                         pads)
        return location

    def __ParseMissionList(self, missionListJSON):
        missions = []
        for missionJSON in missionListJSON:
            missionAgencies = []
            if missionJSON['agencies'] is not None:
                for agencyJSON in missionJSON['agencies']:
                    agency = self.__ParseAgency(agencyJSON)
                    missionAgencies.append(agency)

            missionKeys = ['id',
                           'name',
                           'description',
                           'type',
                           'typeName',
                           'wikiURL']
            mission = self.__Mission(*self.__ParseObject(missionJSON,
                                                         missionKeys),
                                     missionAgencies)
            missions.append(mission)
        return missions

    def __ParseLSP(self, LSPJSON):
        if isinstance(LSPJSON, dict):
            LSPKeys = ['id',
                       'name',
                       'abbrev',
                       'countryCode',
                       'wikiURL']
            LSP = self.__LSP(*self.__ParseObject(LSPJSON, LSPKeys))
            return LSP
        else:
            response = self.__APICall("lsp/" + LSPJSON)
            return self.__ParseLSP(response['agencies'][0])

    def __ParseLaunches(self, launchesJSON):
        launchEvents = []
        for launchJSON in launchesJSON:
            id = int(launchJSON['id'])
            name = launchJSON['name']
            videoURLs = launchJSON['vidURLs']

            window = self.__ParseLaunchWindow(launchJSON)
            status = self.__ParseLaunchStatus(launchJSON)

            try:
                rocket = self.__ParseRocket(launchJSON['rocket'])
            except KeyError:
                rocket = None

            try:
                location = self.__ParseLocation(launchJSON['location'])
            except KeyError:
                location = None

            try:
                missions = self.__ParseMissionList(launchJSON['missions'])
            except KeyError:
                missions = None

            try:
                lsp = self.__ParseLSP(launchJSON['lsp'])
            except KeyError:
                lsp = None

            launchEvent = self.__LaunchEvent(id, name, videoURLs, window,
                                             status, rocket, location,
                                             missions, lsp)
            launchEvents.append(launchEvent)
        return launchEvents

    # Launches
    def NextLaunch(self):
        # Special case (implemented for simplicity)
        return self.UpcomingLaunches(launchCount=1)[0]

    def UpcomingLaunches(self, launchCount=None, id=None, including=None,
                         after=None, before=None):
        # Form API Call
        endpoint = "launch?mode=verbose"
        if launchCount is not None:
            endpoint += "&next=" + str(launchCount)
        if including is not None:
            endpoint += "&name=" + str(including)
        if id is not None:
            endpoint += "&id=" + str(id)
        if after is not None:
            endpoint += "&startdate=" + after
        if before is not None:
            endpoint += "&enddate=" + before

        response = self.__APICall(endpoint)
        launchEvents = self.__ParseLaunches(response['launches'])
        return launchEvents
