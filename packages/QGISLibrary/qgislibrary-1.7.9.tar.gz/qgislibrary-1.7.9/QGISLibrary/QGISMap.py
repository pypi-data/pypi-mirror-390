import logging
from typing import Any
from .QGISCore import QGISLocator as Lr
from .QGISCore import QGISAction as An


class QGISMapOverlay(An, Lr):
    @staticmethod
    def map_extent_setup(main_window: Any, center_lat: str, center_lon: str, scale: str = '1:10000', epsg: int = 4326) -> None:
        """
        Configure Map Extent.

        == Arguments ==
        - ``main_window``: main_window object.
        - ``center_lat``: center latitude (example 45,6).
        - ``center_lon``: center longitude (example 23,6).
        - ``scale``: scale (default 1:10000).
        - ``epsg``: only epsg 4326 (default 4326).

        == Example ==
        | Map Extent Setup | ${main_window} | 34,5 | 12,5 | 1:20000 |

        == Returns ==
        None
        """
        status_bar = Lr.get_locator_by_parent(main_window, auto_id="QgisApp.statusbar",
                                                         control_type="StatusBar")
        coordinates_textbox = Lr.get_locator_by_path(status_bar.Edit2)
        switch_button = Lr.get_locator_by_path(status_bar.Checkbox1)
        scale_textbox = Lr.get_locator_by_path(status_bar.Edit3)
        logging.info('[SETUP] MAP EXTENT')


        logging.info(f'[ACTION] CENTER LAT: {center_lat}, CENTER LON: {center_lon}, SCALE: {scale}')
        An.clear_type_keys_enter_locator(scale_textbox, scale)
        An.clear_type_keys_enter_locator(coordinates_textbox, center_lat + '{SPACE}' + center_lon)
        An.mouse_left_click_locator(switch_button)
        map_extent_ = Lr.get_locator_texts(coordinates_textbox)[0].split(' ')
        global map_extent
        map_extent = {'map_bottom': float(map_extent_[0].replace(',', '.').replace('°', '')),
                      'map_left': float(map_extent_[2].replace(',', '.').replace('°', '')),
                      'map_top': float(map_extent_[4].replace(',', '.').replace('°', '')),
                      'map_right': float(map_extent_[6].replace(',', '.').replace('°', ''))
                      }
        logging.info(f'[ACTION] MAP EXTENT: {map_extent}')
        An.mouse_left_click_locator(switch_button)

    @staticmethod
    def move_mouse_coords(main_window: Any, lat: str, lon: str, action: str | None, button: str | None = None, sleep_time: int = 0) -> None:
        """
        Move mouse to coordinates with optional click/press/release button left/right.

        == Arguments ==
        - ``main_window``: main_window object.
        - ``lat``: latitude (example 45,6).
        - ``lon``: longitude (example 23,6).
        - ``action``: mouse click or press or release or None (default None).
        - ``button``: mouse button left or right or None (default None).
        - ``sleep_time``: Time to sleep after action (default 0).

        == Example ==
        | Move Mouse Coords | ${main_window} | 34,5 | 12,5 |
        | Move Mouse Coords | ${main_window} | 34,5 | 12,5 | click | right | 1 |
        | Move Mouse Coords | ${main_window} | 34,5 | 12,5 | press | left | 3 |

        == Returns ==
        None
        """
        overlay_group = Lr.get_locator_by_parent(main_window, auto_id="QgisApp.centralwidget",
                                                            control_type="Group")
        map_overlay = Lr.get_locator_by_path(overlay_group.Custom2)

        map_rectangle_ = map_overlay.rectangle()
        map_height_ = map_overlay.rectangle().height()
        map_width_ = map_overlay.rectangle().width()
        map_left_ = map_overlay.rectangle().left
        map_right_ = map_overlay.rectangle().right
        map_top_ = map_overlay.rectangle().top
        map_bottom_ = map_overlay.rectangle().bottom
        map_mid_point_ = map_overlay.rectangle().mid_point().x, map_overlay.rectangle().mid_point().y

        logging.info('[SETUP] MOVE MOUSE COORDS')

        # MAP
        map_bottom = map_extent.get('map_bottom')
        map_left = map_extent.get('map_left')
        map_top = map_extent.get('map_top')
        map_right = map_extent.get('map_right')

        map_height = map_top - map_bottom
        map_width = map_right - map_left

        # SCREEN
        screen_height = map_height_
        screen_width = map_width_

        # FACTOR
        factor_height = float(screen_height) / map_height
        factor_width = float(screen_width) / map_width

        # MAP
        lat = float(lat.replace(',', '.').replace('°', ''))
        lon = float(lon.replace(',', '.').replace('°', ''))
        start_lat = map_bottom
        start_lon = map_left

        diff_lat = lat - start_lat
        diff_lon = lon - start_lon

        # SCREEN
        start_X = map_left_
        start_Y = map_bottom_

        global X, Y
        X = int(start_X) + int(diff_lon * factor_width)
        Y = int(start_Y) - int(diff_lat * factor_height)

        # MOUSE
        An.move_mouse_coords(X, Y, sleep_time=sleep_time)
        if action == 'click':
            An.mouse_click_coords(X, Y, button=button, sleep_time=sleep_time)
        if action == 'press':
            An.mouse_press_coords(X, Y, button=button, sleep_time=sleep_time)
        if action == 'release':
            An.mouse_release_coords(X, Y, button=button, sleep_time=sleep_time)
