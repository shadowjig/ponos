import soco

SONOS_DEBUG = False

def get_a_speaker():
    topology = soco.discover(timeout=5, include_invisible=False)
    return topology.pop()

def get_zones():
    myspeaker = get_a_speaker()
    if SONOS_DEBUG: print("\nmyspeaker: " + myspeaker.player_name)
    zones = myspeaker.all_groups

    if SONOS_DEBUG: print(zones)
    if SONOS_DEBUG: print("\n")
    zone_list = []
    for zone in zones:
        need_coord = False
        count = 0
        mem_list = []

        
        if zone.coordinator == None:
            need_coord = True
            if SONOS_DEBUG: print("Need coord")
        else:   
            coord = zone.coordinator
            if SONOS_DEBUG: print("Don't need coord")
            count -= 1
            
        for member in zone.members:
            if member.is_bridge == False:
                if need_coord == True:
                    coord = member
                    need_coord = False
                else:
                    if member.player_name != coord.player_name:
                        mem_list.append(member.player_name)
                    count += 1
                    
        if coord.is_bridge == False:
            short_name = coord.player_name
            if count > 0:
                short_name += " + " + str(count)
            zone_list.append({'coordinator' : coord.player_name, 'short_name': short_name, 'num_members' : count, 'members': mem_list})

    zone_list = sorted(zone_list, key=lambda k: k['short_name']) 
    if SONOS_DEBUG: print(zone_list)
    return zone_list

def zone_play(zone_member, media_uri):
    myspeaker = get_a_speaker()
    if SONOS_DEBUG: print("myspeaker: " + myspeaker.player_name)
    zones = myspeaker.all_groups
    
    for zone in zones:
        for member in zone.members:
            if member.player_name == zone_member:
                return member.play_uri(media_uri)
    return False

def getSec(s):
    l = s.split(':')
    return int(l[0]) * 3600 + int(l[1]) * 60 + int(l[2])
    
def get_track(selected_zone):
    myspeaker = get_a_speaker()
    zones = myspeaker.all_groups
    
    for zone in zones:
        for member in zone.members:
            if member.player_name == selected_zone:
                rv = member.get_current_track_info()
                if (not(rv['duration'] == 'NOT_IMPLEMENTED')) and (not(rv['duration'] == 'NOT_IMPLEMENTED')):
                    rv['duration_secs'] = getSec(rv['duration'])
                    rv['current_secs'] = getSec(rv['position'])
                    if rv['duration_secs'] != 0:
                        rv['precent'] = 100 * (rv['current_secs']/rv['duration_secs'])
                    else:
                        rv['precent'] = 0
                else:
                    rv['duration_secs'] = 0
                    rv['current_secs'] = 0
                    rv['precent'] = 0
                if member.mute == True:
                    rv['state_muted'] = 1
                else:
                    rv['state_muted'] = 0
                    
                if member.get_current_transport_info()['current_transport_state'] == 'PLAYING':
                    rv['state_playing'] = 1
                else:
                    rv['state_playing'] = 0
                if SONOS_DEBUG: print('track data = ', rv)
                return rv
    return False
 
def mute_zone(zone_member):
    if SONOS_DEBUG: print("Inside mute")
    myspeaker = get_a_speaker()
    if SONOS_DEBUG: print("myspeaker: " + myspeaker.player_name)
    zones = myspeaker.all_groups
    
    for zone in zones:
        for member in zone.members:
            if member.player_name == zone_member:
                member.mute = True
                if member.mute == True:
                    return True
                else:
                    return False
    return False

def unmute_zone(zone_member):
    if SONOS_DEBUG: print("Inside unmute")
    myspeaker = get_a_speaker()
    if SONOS_DEBUG: print("myspeaker: " + myspeaker.player_name)
    zones = myspeaker.all_groups
    
    for zone in zones:
        for member in zone.members:
            if member.player_name == zone_member:
                member.mute = False
                if member.mute == False:
                    return True
                else:
                    return False
    return False
    
def play(zone_member):
    if SONOS_DEBUG: print("Inside play")
    myspeaker = get_a_speaker()
    if SONOS_DEBUG: print("myspeaker: " + myspeaker.player_name)
    zones = myspeaker.all_groups
    
    for zone in zones:
        for member in zone.members:
            if member.player_name == zone_member:
                return member.play()

    return False
    
def pause(zone_member):
    if SONOS_DEBUG: print("Inside pause")
    myspeaker = get_a_speaker()
    if SONOS_DEBUG: print("myspeaker: " + myspeaker.player_name)
    zones = myspeaker.all_groups
    
    for zone in zones:
        for member in zone.members:
            if member.player_name == zone_member:
                return member.pause()

    return False
   
def skipback(zone_member, timestamp):
    if SONOS_DEBUG: print("Inside skipback")
    myspeaker = get_a_speaker()
    if SONOS_DEBUG: print("myspeaker: " + myspeaker.player_name)
    if SONOS_DEBUG: print("myspeaker: " + myspeaker.player_name)
    zones = myspeaker.all_groups
    
    for zone in zones:
        for member in zone.members:
            if member.player_name == zone_member:
                if SONOS_DEBUG: print('player_name= ' + member.player_name)
                if SONOS_DEBUG: print('timestamp= ' + str(timestamp))
                member.seek(str(timestamp))
                return True
    return False

