import math
from nicegui import ui
#import qrcode
import os

import requests

from nicegui import app, ui

from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException
from fastapi.responses import HTMLResponse

# bib of sign

import logging
import time
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Request
from starlette.responses import RedirectResponse

from pathlib import Path


SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzxgfdR12nLIMd0Nwaf-xfpcysxIDi7UST_o9DhlL2ryO9nCRvyA-XgwIstimL9KsY_vA/exec"

def save_user(user):

    r = requests.post(
        SCRIPT_URL,
        json={
            "action": "save_user",
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
        },
        timeout=10,
    )

    return r.json()




def request_access(user_id):

    requests.post(
        SCRIPT_URL,
        json={
            "action": "request_access",
            "id": user_id,
        },
        timeout=10,
    )




def get_status(user_id):

    r = requests.post(
        SCRIPT_URL,
        json={
            "action": "get_status",
            "id": user_id,
        },
        timeout=10,
    )

    data = r.json()

    if not data.get("exists"):
        return None

    if data.get("banned"):
        return "banned"

    return data["status"]



GOOGLE_CLIENT_ID = '978983798994-fg6e83cm1aol6700kes5odfcsl4gur35.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
 
oauth = OAuth()
oauth.register(
            name='google',
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            client_kwargs={'scope': 'openid email profile'},
        )

def _is_valid(user_info: dict) -> bool:
    try:
        return all([
            int(user_info.get('exp', 0)) > int(time.time()),
            user_info.get('aud') == GOOGLE_CLIENT_ID,
            user_info.get('iss') in {'https://accounts.google.com', 'accounts.google.com'},
            str(user_info.get('email_verified')).lower() == 'true',
        ])
    except Exception:
        return False
 
def logout() -> None:
    app.storage.user.pop('user_info', None)
    ui.navigate.to('/')





@ui.page('/')
def main():

    #qr_code = qrcode.make('https://www.google.com')
    #qr_code.save('qr_code.png')

    ui.add_head_html('''
<style>

.nicegui-content {
    margin: 0;
    padding: 0;
}

body {
    font-family: "Poppins";
    font-weight: bold;
    
    padding: 0;
    user-select: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    background-color: black;
}
</style>
''')

    ui.add_head_html('''
<style>
.numbers .q-field__native,
.numbers .q-field__input{
    padding-left: 20px;
}
</style>
''')

    ui.add_head_html('''
<style>
.input-label .q-field__label {
    padding-left: 20px;
}
</style>
''')

    ui.add_head_html('''
<style>
/* Scrollbar width */
::-webkit-scrollbar {
    width: 15px;
}

/* Background */
::-webkit-scrollbar-track {
    background: #262626;
}

/* The moving part */
::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
}

/* Hover */
::-webkit-scrollbar-thumb:hover {
    background: #555;
}



</style>
''')


    ui.add_head_html('''
<style>
.q-drawer {
    background: rgba(0,0,0,0.15) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}
</style>
''')



    #IMAGES_DIR = r"C:\Users\x\Documents\ANACONDA TP\CHARPENTE_PRGRM\justfortesting Qtpy\nicegui"
    
    BASE_DIR = Path(__file__).parent
    app.add_static_files('/filez', BASE_DIR / 'filez')


    with ui.left_drawer(value=False).props('behavior=mobile overlay').classes('q-drawer') as drawer:
        #behavior=mobile overlay
        
        ui.label('We work on it as soon as possible').style('color:white').props('offset=[0,300]')

            #.props('offset=[0,100]')

#.style('background-color:#1A1A1A ')
    with ui.header().style('z-index:9999; background: rgba(0,0,0,0.15); box-shadow: 0 4px 20px rgba(0,0,0,0.15); backdrop-filter: blur(10px);').classes('items-center justify-between'):

        with ui.row().classes('items-center'):
            ui.button(icon='menu', on_click=drawer.toggle).style('border-radius:100px;').props('flat color=white')
            with ui.row():
                ui.label('Civeng Cal').style('color:white')

        with ui.row().classes('items-center'):
            ui.image('/filez/logogoftest.gif').style('width:45px')

            user_info = app.storage.user.get('user_info', {})
            logged_in = _is_valid(user_info)

            if not logged_in:
                app.storage.user.pop('user_info', None)
                status = None

            else:
                result = save_user({
                    "id": user_info["sub"],
                    "email": user_info["email"],
                    "name": user_info["name"],
                })

                if result["banned"]:
                    app.storage.user.pop("user_info", None)
                    ui.notify("Your account has been banned.", color="negative")
                    ui.navigate.reload()
                    return

                status = result["status"]
        
            if logged_in:
                with ui.button(icon='account_circle').props('round flat color=white size=15px') as btn:
                    with ui.menu().style('padding:20px; color:white; z-index:9999; background: rgba(0,0,0,0.15); box-shadow: 0 4px 20px rgba(0,0,0,0.15); backdrop-filter: blur(10px); border-radius:15px;').props('offset=[0,30]').classes('w-fit h-fit'):
                        with ui.column().classes('w-full h-full items-center justify-center'):
                            ui.image(user_info['picture']).style('width:60px; height:60px; border-radius:50%; object-fit:cover; border:2px solid white;')
                            #.classes('w-fit h-fit')
                            ui.label(user_info['name'])
                            ui.label(user_info['email'])
                            ui.button('Sign out',icon='logout',on_click=logout).style('background-color:#FF4800 ; text-transform: none; border-radius:100px; box-shadow: 0 8px 25px rgba(255, 72, 0, 0.45);').props('flat color=white')

            
                        
 
            

        

    




    #.style('width:40px; background-color:white; padding:10px; border-radius:10px')
#z-index:9999;

#background: rgba(255,255,255,0.15);     backdrop-filter: blur(15px);
    #420DF2

#content
    with ui.column().style('padding:10px').classes('w-full'):
#background: linear-gradient(135deg, #1A1A1A, #262626 );
        with ui.carousel(animated=True).classes('w-fit').style('background:linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.7)),url("/filez/steel_frame_strusture.png"); background-position: center top;background-repeat: no-repeat;  color:white ;width: 100%; border-radius:25px ; box-shadow: 0 50px 200px rgba(66, 13, 242, 0.4)'):
            #background-size: cover;
            with ui.carousel_slide().classes('w-full'):
                with ui.column().classes('w-full h-full items-center justify-center'):
                    ui.label('Share it :/')
                #ui.image(r'C:\Users\x\Documents\ANACONDA TP\CHARPENTE_PRGRM\justfortesting Qtpy\windlogo3339new.ico').style('width:50px')
                    ui.image('/filez/qr_code.png').style('width:150px; border-radius:25px;')
                    ui.label('/Direction of Pr. Hamid Hamli Ben Zahar')
                    ui.label('/Developed by Mr. Rebouh Abdelbasat')
                    
                    #ui.label('This app make you calculate & inject wind load by the esiest way possible, Sign now work simple').classes('text-center').style('padding-top:0px').classes('w-fit')
                    if logged_in:
                        with ui.row():
                            #ui.button('Download Cnc Cal').style('background-color:#420DF2 ; font-weight: bold; text-transform: none; border-radius:100px; box-shadow: 0 8px 25px rgba(66, 13, 242, 0.45);').props('flat color=white')
                            #ui.button('Request Access',on_click=lambda: (request_access(user_info['sub']),ui.notify('Access request sent.', color='positive'))).style('background-color:#22C55E ; font-weight: bold; text-transform: none; border-radius:100px; box-shadow:0 8px 25px rgba(34,197,94,0.45);').props('flat color=white')
                            if status == 'not_requested':
                                ui.button('Request Access',on_click=lambda: (request_access(user_info['sub']),ui.notify('Access request sent.', color='positive'),ui.navigate.reload())).style('background-color:#22C55E ; font-weight: bold; text-transform: none; border-radius:100px; box-shadow:0 8px 25px rgba(34,197,94,0.45);').props('flat color=white')

                            elif status == 'pending':ui.button('Pending...',).props('disable').style('background-color:#22C55E ; font-weight: bold; text-transform: none; border-radius:100px; box-shadow:0 8px 25px rgba(34,197,94,0.45);').props('flat color=white')

                            elif status == 'approved':ui.button('Download CNC Cal').style('background-color:#420DF2 ; font-weight: bold; text-transform: none; border-radius:100px; box-shadow: 0 8px 25px rgba(66, 13, 242, 0.45);').props('flat color=white')

                    if not logged_in:
                        ui.button(on_click=lambda: ui.navigate.to('/login')).style('text-transform: none; background-color:white ;background-image: url("/filez/google.jpg");background-size: contain;background-position: center;background-repeat: no-repeat; border-radius:100px; width:120px; box-shadow: 0 8px 25px rgba(255, 255, 255, 0.45);').props('flat color=black')
#'Sign in',icon='login',
                    #ui.label('_updates: we enhanced the adding features v0.1 ').classes('text-center').style('color:red; padding-top:0px; background-color:white')

    with ui.column().style('padding:10px; width: 100%; min-width: 0;'):
        ui.label('➥ About us:').style('color:white').classes('w-full items-center justify-between')
        ui.label("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since 1966, when designers at Letraset and James Mosley, the librarian at St Bride Printing Library in London, took a 1914 Cicero translation and scrambled it to make dummy text for Letraset's Body Type sheets. It has survived not only many decades, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised thanks to these sheets and more recently with desktop publishing software like Aldus PageMaker and Microsoft Word including versions of Lorem Ipsum.").style('''
        white-space: pre-wrap;
        color: white;
        text-align: justify;
    ''').classes('w-full')


    










    if logged_in and status == 'approved':
        with ui.element().style('padding:10px').classes('w-full'):
            ui.label('Main app:').style('color:white')
            ui.label('➤ Wind load: W0-1, W0-2, W90, W180-1, W180-2, W270').style('color:white').classes('w-full')

           # ui.number('hp?',value=0 ,min=0).props('outlined rounded dark color=white').style('width:100px; color:white').classes('numbers').classes('input-label')

        with ui.column().style('padding:10px').classes('w-full'):
            ui.label('➥ Project Geo:').style('color:white').classes('items-center justify-between')
            with ui.grid(columns=2).classes('w-full flex-nowrap'):
                ht = ui.number('ht?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')
                hp = ui.number('hp?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')
                w = ui.number('w?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')
                l = ui.number('l?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')
        with ui.column().style('padding:10px').classes('w-full'):
            ui.label('➥ Open Area:').style('color:white').classes('items-center justify-between')
            with ui.grid(columns=2).classes('w-full flex-nowrap'):
                s0 = ui.number('s0?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')
                s90 = ui.number('s90?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')
                s180 = ui.number('s180?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')
                s270 = ui.number('s270?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')
        with ui.column().style('padding:10px').classes('w-full'):
            ui.label('➥ Cladding Num:').style('color:white').classes('items-center justify-between')
            with ui.grid(columns=2).classes('w-full flex-nowrap'):
                p0 = ui.number('p0?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')
                t0 = ui.number('t0?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')
                
                p180 = ui.number('p180?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')
                t180 = ui.number('t180?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')

                p90 = ui.number('p90?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')
                p270 = ui.number('p270?' ,min=0).props('outlined rounded dark color=white').style('color:white').classes('flex-1')

        with ui.column().style('padding:10px').classes('w-full'):
            ui.label('➥ Wind Zone & Terrain:').style('color:white').classes('items-center justify-between')
            zone_data = {
                "WIND ZONE I" : { "qref": 37.5},
                "WIND ZONE II" : { "qref": 43.5},
                "WIND ZONE III" : { "qref": 50},
                "WIND ZONE IV" : { "qref": 57.5},
            }

            
            terrain_data = {
                "TERRAIN 0": {"z1": 1.811, "z2": 2.137, "z5": 2.603, "z10": 2.983, "z15": 3.216, "z20": 3.387, "z25": 3.521, "z30": 3.633, "z35": 3.729, "z40": 3.813, "z50": 3.956, "z60": 4.074, "z70": 4.175, "z80": 4.264, "z100": 4.414, "z125": 4.566, "z150": 4.692, "z175": 4.800, "z200": 4.895},
                "TERRAIN I": {"z1": 1.545, "z2": 1.883, "z5": 2.373, "z10": 2.776, "z15": 3.025, "z20": 3.207, "z25": 3.352, "z30": 3.472, "z35": 3.575, "z40": 3.666, "z50": 3.820, "z60": 3.947, "z70": 4.056, "z80": 4.152, "z100": 4.315, "z125": 4.480, "z150": 4.617, "z175": 4.735, "z200": 4.838},
                "TERRAIN II": {"z1": 1.423, "z2": 1.423, "z5": 1.929, "z10": 2.352, "z15": 2.616, "z20": 2.810, "z25": 2.965, "z30": 3.094, "z35": 3.205, "z40": 3.302, "z50": 3.468, "z60": 3.606, "z70": 3.725, "z80": 3.829, "z100": 4.006, "z125": 4.187, "z150": 4.337, "z175": 4.466, "z200": 4.579},
                "TERRAIN III": {"z1": 1.276, "z2": 1.276, "z5": 1.276, "z10": 1.703, "z15": 1.973, "z20": 2.174, "z25": 2.335, "z30": 2.470, "z35": 2.587, "z40": 2.690, "z50": 2.865, "z60": 3.012, "z70": 3.139, "z80": 3.250, "z100": 3.440, "z125": 3.634, "z150": 3.796, "z175": 3.936, "z200": 4.058},
                "TERRAIN IV": {"z1": 1.173, "z2": 1.173, "z5": 1.173, "z10": 1.173, "z15": 1.440, "z20": 1.640, "z25": 1.801, "z30": 1.937, "z35": 2.055, "z40": 2.159, "z50": 2.337, "z60": 2.487, "z70": 2.617, "z80": 2.731, "z100": 2.926, "z125": 3.127, "z150": 3.295, "z175": 3.440, "z200": 3.568},
            }
            

            with ui.row().classes('w-full'):
                zone = ui.select(options=list(zone_data.keys()),value='WIND ZONE I',label='Zone').props('outlined dark color=white').classes('w-full')
                terrain = ui.select(options=list(terrain_data.keys()),value='TERRAIN 0',label='Terrain').props('outlined dark color=white').classes('w-full')




            def read_inputs():

                c = math.atan(ht.value / (w.value / 2))
                a = math.degrees(c)
                    
            
                h = ht.value + hp.value
            
                d1 = math.cos(c)
                d2 = math.sin(c)
                d3 = math.tan(c)

                return h, a, d1, d2, d3



            def ce(terrain,h):
            
                    read_inputs()
            
                    data = terrain_data[terrain]
                    points = sorted(
                        (int(k[1:]), v) for k, v in data.items()
                )
            
                # Exact value
                    for z, value in points:
                        if h == z:
                            return value
            
                # Limits
                    if h <= points[0][0]:
                        return points[0][1]
            
                    if h >= points[-1][0]:
                        return points[-1][1]
            
                # Linear interpolation
                    for (z1, v1), (z2, v2) in zip(points[:-1], points[1:]):
                        if z1 <= h <= z2:
                            return v1 + (v2 - v1) * (h - z1) / (z2 - z1)
            
            
            
            def get_zone_qref(zone):
                return zone_data[zone.value]["qref"]




            def inject():
                try:
                    h, a, d1, d2, d3 = read_inputs()
                    ce_value = ce(terrain.value, h)
                    qref = get_zone_qref(zone)

                    result_label.set_text(
                        f'les donnes\nh={h:.3f}, α={a:.3f}, qref={qref:.3f}, ce={ce_value:.3f}'
                    )

                except:
                    result_label.set_text(f'Error')   

                #except Exception as e:
                    #result_label.set_text(f'Error: {e}')


            


















        with ui.column().style('padding:10px').classes('w-full'):
            ui.label('➥ Cladding Legende:').style('color:white').classes('items-center justify-between')
            with ui.element().style('border-radius:25px; overflow:hidden').classes('w-full'):
                #overflow:hidden
                #app.add_static_files('/models', r'C:\Users\x\Documents\ANACONDA TP\CHARPENTE_PRGRM\justfortesting Qtpy\nicegui')
                with ui.scene(fps=120,camera=ui.scene.orthographic_camera(size=3.5),background_color='#222',grid=(1, 1)).classes('w-full') as scene:
            #scene.axes_helper()
                    model = scene.gltf('/filez/scene333.glb')
                    model.scale(1)
                    model.rotate(1.57, 0, 0)
                    model.move(0, 0, 0)  
                    scene.move_camera(x=-5, y=-6, z=4)
            #scene.gltf('/models/scene333.glb')
            #scene.move_camera(x=1, y=-1, z=1.5, duration=2)
            
        with ui.column().style('padding:10px').classes('w-full'):
            ui.label('➥ Inject & Result:').style('color:white')

#Result
            with ui.row().style('padding:20px;color:white; border: 1px solid white; border-radius: 25px').classes('w-full h-fit'):
                result_label = ui.label().style('white-space: pre-wrap; user-select: text')
            
            ui.button('Inject & Calculate', on_click=inject).style('font-weight: bold;background-color:#420DF2 ; text-transform: none; border-radius:100px; box-shadow: 0 8px 25px rgba(66, 13, 242, 0.45); margin-left:auto').props('flat color=white')




    with ui.element().style('background: #1A1A1A').classes('items-center justify-between w-full'):
        ui.label('All the rights reserved').style('color:white').style('padding-top:10px').classes('text-center')
        ui.label('2026-2027').style('color:white').style('padding-bottom:10px').classes('text-center')


    #app.add_static_files(
    #    '/assets',
    #    r'C:\Users\x\Documents\ANACONDA TP\CHARPENTE_PRGRM\justfortesting Qtpy'
    #)




@ui.page('/login')
async def login(request: Request) -> RedirectResponse:
    return await oauth.google.authorize_redirect(request, request.url_for('google_oauth'))


@app.get('/auth')
async def google_oauth(request: Request) -> RedirectResponse:
    try:
        user_info = (await oauth.google.authorize_access_token(request)).get('userinfo', {})
        #print("USER INFO:", user_info)
        #print("VALID?", _is_valid(user_info))
        if _is_valid(user_info):
            app.storage.user['user_info'] = user_info

            # هنا
            save_user({
                'id': user_info['sub'],
                'email': user_info['email'],
                'name': user_info['name'],
            })

    except (OAuthError, Exception):
        logging.exception('could not authorize access token')
    return RedirectResponse('/')



  
#import secrets

#print(secrets.token_hex(32))

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(host='0.0.0.0',port=int(os.environ.get('PORT', 8080)), storage_secret='aa4c0deafc3e66b1ce6d18efa52a0d6a4e96ceb5c18ebed69282375632062447', title='Rnv Calc', favicon=r'C:\Users\x\Documents\ANACONDA TP\CHARPENTE_PRGRM\justfortesting Qtpy\windlogo3339new.ico')
