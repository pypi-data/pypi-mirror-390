from nicegui import app, ui

from biblemateweb import BIBLEMATEWEB_APP_DIR

from biblemateweb.pages.original.reader import original_reader
from biblemateweb.pages.original.interlinear import original_interlinear
from biblemateweb.pages.original.parallel import original_parallel
from biblemateweb.pages.original.discourse import original_discourse
from biblemateweb.pages.original.linguistic import original_linguistic

from biblemateweb.pages.bibles.audio import bibles_audio

import os

# --- Shared Menu Function ---
# This function creates the header, horizontal menu (desktop),
# and drawer (mobile).

def create_menu():
    """Create the responsive header and navigation drawer."""
    
    # TODO: Consider dark mode latter
    # Dark Mode
    # ui.dark_mode().toggle()
    
    # Use app.storage.user to store session-specific state
    # This keeps the drawer state unique for each user
    app.storage.user.setdefault('left_drawer_open', False)

    # --- Header ---
    with ui.header(elevated=True).classes('bg-primary text-white'):
        # We use 'justify-between' to push the left and right groups apart
        with ui.row().classes('w-full items-center justify-between no-wrap'):
            
            # --- Left Aligned Group ---
            with ui.row().classes('items-center no-wrap'):
                # --- Hamburger Button (Mobile Only) ---
                # This button toggles the 'left_drawer_open' value in user storage
                # .classes('lt-sm') means "visible only on screens LESS THAN Medium"
                ui.button(
                    on_click=lambda: app.storage.user.update(left_drawer_open=not app.storage.user['left_drawer_open']),
                    icon='menu'
                ).props('flat color=white').classes('lt-sm')

                # --- Mobile Avatar Button (Home) ---
                # This is a button that contains the avatar
                with ui.button(on_click=lambda: ui.navigate.to('/')).props('flat round dense').classes('lt-sm'):
                    with ui.avatar(size='32px'):
                         with ui.image(os.path.join(BIBLEMATEWEB_APP_DIR, 'eliranwong.jpg')) as image:
                            with image.add_slot('error'):
                                ui.icon('account_circle').classes('m-auto') # Center fallback icon

                # --- Desktop Avatar + Title (Home) ---
                # The button contains a row with the avatar and the label
                with ui.button(on_click=lambda: ui.navigate.to('/')).props('flat text-color=white').classes('gt-xs'):
                    with ui.row().classes('items-center no-wrap'):
                        # Use a fallback icon in case the image fails to load
                        with ui.avatar(size='32px'):
                            with ui.image(os.path.join(BIBLEMATEWEB_APP_DIR, 'eliranwong.jpg')) as image:
                                with image.add_slot('error'):
                                    ui.icon('account_circle').classes('m-auto') # Center fallback icon
                        
                        # This is just a label now; the parent button handles the click
                        ui.label('BibleMate AI').classes('text-lg ml-2') # Added margin-left for spacing

            # --- Right Aligned Group (Features & About Us) ---
            with ui.row().classes('items-center no-wrap'):
                
                # --- Desktop Menu (Features & About) ---
                # This row contains buttons only visible on desktop
                with ui.row().classes('gt-xs items-center no-wrap'):
                    # Original Bible Suite
                    with ui.button('Original').props('flat color=white'):
                        with ui.menu():
                            ui.menu_item('Original Reader’s Bible', on_click=lambda: ui.navigate.to('/original/reader'))
                            ui.menu_item('Original Interlinear Bible', on_click=lambda: ui.navigate.to('/original/interlinear'))
                            ui.menu_item('Original Parallel Bible', on_click=lambda: ui.navigate.to('/original/parallel'))
                            ui.menu_item('Original Discourse Bible', on_click=lambda: ui.navigate.to('/original/discourse'))
                            ui.menu_item('Original Linguistic Bible', on_click=lambda: ui.navigate.to('/original/linguistic'))

                    # Bible
                    with ui.button('Bibles').props('flat color=white'):
                        with ui.menu():
                            ui.menu_item('Bible Chapter', on_click=lambda: ui.navigate.to('/bibles/chapter'))
                            ui.menu_item('Bible Verse', on_click=lambda: ui.navigate.to('/bibles/verse'))
                            ui.menu_item('Bible Audio', on_click=bibles_audio)
                            ui.menu_item('Compare Chapter', on_click=lambda: ui.navigate.to('/compare/chapter'))
                            ui.menu_item('Compare Verse', on_click=lambda: ui.navigate.to('/compare/verse'))

                    # Bible Tools
                    with ui.button('Tools').props('flat color=white'):
                        with ui.menu():
                            ui.menu_item('Bible Commentaries', on_click=lambda: ui.navigate.to('/tool/commentary'))
                            ui.menu_item('Cross-references', on_click=lambda: ui.navigate.to('/tool/xref'))
                            ui.menu_item('Treasury of Scripture Knowledge', on_click=lambda: ui.navigate.to('/tool/tske'))
                            ui.menu_item('Discourse Analysis', on_click=lambda: ui.navigate.to('/tool/discourse'))
                            ui.menu_item('Morphological Data', on_click=lambda: ui.navigate.to('/tool/morphology'))
                            ui.menu_item('Translation Spectrum', on_click=lambda: ui.navigate.to('/tool/translations'))
                            ui.menu_item('Bible Timelines', on_click=lambda: ui.navigate.to('/tool/timelines'))
                            ui.menu_item('Bible Chronology', on_click=lambda: ui.navigate.to('/tool/chronology'))
                
                # --- Mobile "About Us" Icon Button ---
                # This button is only visible on mobile

                with ui.button(icon='book').props('flat color=white round'):
                    with ui.menu():
                        ...

                with ui.button(icon='book').props('flat color=white round'):
                    with ui.menu():
                        ...
                
                with ui.button(icon='search').props('flat color=white round'):
                    with ui.menu():
                        ui.menu_item('Bibles', on_click=lambda: ui.navigate.to('/search/bible'))
                        ui.menu_item('Parallels', on_click=lambda: ui.navigate.to('/search/parallels'))
                        ui.menu_item('Promises', on_click=lambda: ui.navigate.to('/search/promises'))
                        ui.menu_item('Topics', on_click=lambda: ui.navigate.to('/search/topics'))
                        ui.menu_item('Names', on_click=lambda: ui.navigate.to('/search/names'))
                        ui.menu_item('Characters', on_click=lambda: ui.navigate.to('/search/characters'))
                        ui.menu_item('Locations', on_click=lambda: ui.navigate.to('/search/locations'))
                        ui.menu_item('Dictionary', on_click=lambda: ui.navigate.to('/search/dictionary'))
                        ui.menu_item('Encyclopedia', on_click=lambda: ui.navigate.to('/search/encyclopedia'))
                        ui.menu_item('Lexicon', on_click=lambda: ui.navigate.to('/search/lexicon'))

                with ui.button(icon='thumb_up').props('flat color=white round'):
                    with ui.menu():
                        ui.menu_item('AI Commentary', on_click=lambda: ui.navigate.to('/ai/commentary'))
                        ui.menu_item('AI Q&A', on_click=lambda: ui.navigate.to('/ai/qna'))
                        ui.menu_item('AI Chat', on_click=lambda: ui.navigate.to('/ai/chat'))
                        ui.menu_item('Partner Mode', on_click=lambda: ui.navigate.to('/ai/partner'))
                        ui.menu_item('Agent Mode', on_click=lambda: ui.navigate.to('/ai/agent'))

    # --- Drawer (Mobile Menu) ---
    # This section is unchanged
    with ui.drawer('left') \
            .classes('lt-sm') \
            .props('overlay') \
            .bind_value(app.storage.user, 'left_drawer_open') as left_drawer:
        
        ui.label('Navigation').classes('text-xl p-4')

        # Home Link
        ui.item('Home', on_click=lambda: (
            ui.navigate.to('/'),
            app.storage.user.update(left_drawer_open=False)
        )).props('clickable')

        # Original Bible Suite
        with ui.expansion('Original', icon='book').props('header-class="text-primary"'):
            ui.item('Original Reader’s Bible', on_click=lambda: (
                ui.navigate.to('/original/reader'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Original Interlinear Bible', on_click=lambda: (
                ui.navigate.to('/original/interlinear'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Original Parallel Bible', on_click=lambda: (
                ui.navigate.to('/original/parallel'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Original Discourse Bible', on_click=lambda: (
                ui.navigate.to('/original/discourse'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Original Linguistic Bible', on_click=lambda: (
                ui.navigate.to('/original/linguistic'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')

        # Bibles
        with ui.expansion('Bibles', icon='book').props('header-class="text-primary"'):
            ui.item('Bible Chapter', on_click=lambda: (
                ui.navigate.to('/bibles/chapter'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Bible Verse', on_click=lambda: (
                ui.navigate.to('/bibles/verse'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Bible Audio', on_click=lambda: (
                ui.navigate.to('/bibles/audio'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Compare Chapter', on_click=lambda: (
                ui.navigate.to('/compare/chapter'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Compare Verse', on_click=lambda: (
                ui.navigate.to('/compare/verse'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')

        # Bible Tools
        with ui.expansion('Tools', icon='build').props('header-class="text-primary"'):
            ui.item('Bible Commentaries', on_click=lambda: (
                ui.navigate.to('/tool/commentary'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Cross-references', on_click=lambda: (
                ui.navigate.to('/tool/xref'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Treasury of Scripture Knowledge', on_click=lambda: (
                ui.navigate.to('/tool/tske'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Discourse Analysis', on_click=lambda: (
                ui.navigate.to('/tool/discourse'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Morphological Data', on_click=lambda: (
                ui.navigate.to('/tool/morphology'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Translation Spectrum', on_click=lambda: (
                ui.navigate.to('/tool/translations'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Bible Timelines', on_click=lambda: (
                ui.navigate.to('/tool/timelines'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Bible Chronology', on_click=lambda: (
                ui.navigate.to('/tool/chronology'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')

        # Search
        with ui.expansion('Search', icon='search').props('header-class="text-primary"'):
            ui.item('Bibles', on_click=lambda: (
                ui.navigate.to('/search/bible'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Parallels', on_click=lambda: (
                ui.navigate.to('/search/parallels'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Promises', on_click=lambda: (
                ui.navigate.to('/search/promises'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Topics', on_click=lambda: (
                ui.navigate.to('/search/topics'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Names', on_click=lambda: (
                ui.navigate.to('/search/names'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Characters', on_click=lambda: (
                ui.navigate.to('/search/characters'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Locations', on_click=lambda: (
                ui.navigate.to('/search/locations'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Dictionary', on_click=lambda: (
                ui.navigate.to('/search/dictionary'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Encyclopedia', on_click=lambda: (
                ui.navigate.to('/search/encyclopedia'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Lexicon', on_click=lambda: (
                ui.navigate.to('/search/lexicon'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
        
        # AI
        with ui.expansion('AI', icon='thumb_up').props('header-class="text-primary"'):
            ui.item('AI Commentary', on_click=lambda: (
                ui.navigate.to('/ai/commentary'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('AI Q&A', on_click=lambda: (
                ui.navigate.to('/ai/qna'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('AI Chat', on_click=lambda: (
                ui.navigate.to('/ai/chat'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Partner Mode', on_click=lambda: (
                ui.navigate.to('/ai/partner'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Agent Mode', on_click=lambda: (
                ui.navigate.to('/ai/agent'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')

        # About Expansion
        '''with ui.expansion('About Us', icon='info'):
            ui.item('Our Church', on_click=lambda: (
                ui.navigate.to('/about'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Contact', on_click=lambda: (
                ui.navigate.to('/contact'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')'''