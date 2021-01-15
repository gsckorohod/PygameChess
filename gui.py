import pygame

BLACK = pygame.Color('black')
GRAY = pygame.Color('gray')
DARK_GRAY = pygame.Color('#696969')
RED = pygame.Color('red')
BLUE = pygame.Color('blue')

FONT_DS_PATH = 'data/fonts/DS-DIGIB.TTF'
LCD_BG_COLOR = pygame.Color('#aacabe')
LABEL_TEXT_MARGIN = 2

ALIGN_TOP = ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_BOTTOM = ALIGN_RIGHT = 2


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def check_intersection(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    x_ok = ((x2 + w2) >= x1) and (x2 <= (x1 + w1))
    y_ok = ((y2 + h2) >= y1) and (y2 <= (y1 + h1))

    return x_ok and y_ok


def constrain(x, minn, maxn):
    if minn > maxn:
        minn, maxn = maxn, minn

    if x < minn:
        return minn
    elif x < maxn:
        return x
    else:
        return maxn


def mix_color(c1, c2, alpha):
    out = []

    a_value = alpha / 255
    na = 1 - a_value

    for val1, val2 in zip(c1[:3], c2[:3]):
        out.append(min(int(val1 * na + val2 * a_value), 255) % 256)

    out.append(255)

    return tuple(out)


def tint(surface, a=125, color=BLACK):
    new_surface = pygame.Surface((surface.get_width(), surface.get_height()))

    for r in range(surface.get_height()):
        for c in range(surface.get_width()):
            p_color = surface.get_at((c, r))[:3]
            new_col = mix_color(p_color, color, a)
            new_surface.set_at((c, r), new_col)

    return new_surface


class UIElement:
    def __init__(self, rect, img=None, bg_color=GRAY, frame_color=BLACK, frame_w=1):
        self.rect = self.x, self.y, self.w, self.h = list(rect)

        self.bg_color = bg_color
        self.frame_color = frame_color
        self.frame_w = frame_w

        self.is_tinted = False
        self.tint_color = BLACK
        self.tint_alpha = 50

        self.is_hidden = False
        self.is_enabled = True

        self.img = img

    def make_img(self):
        img = pygame.Surface((self.w, self.h))

        margin = self.frame_w // 2

        pygame.draw.rect(img, self.bg_color, (margin,
                                              margin,
                                              self.w - (2 * margin),
                                              self.h - (2 * margin)))

        pygame.draw.rect(img, self.frame_color, (margin,
                                                 margin,
                                                 self.w - (2 * margin),
                                                 self.h - (2 * margin)), self.frame_w)

        return img

    def get_rect(self):
        return self.rect

    def get_height(self):
        return self.h

    def get_pos(self):
        return self.x, self.y

    def get_size(self):
        return self.w, self.h

    def set_pos(self, pos):
        self.x, self.y = self.rect[0], self.rect[1] = pos

    def set_rect(self, rect):
        self.x, self.y, self.w, self.h = self.rect = rect

    def set_size(self, size):
        self.w, self.h = self.rect[2], self.rect[3] = size

    def move(self, dx, dy):
        self.set_pos((self.x + dx, self.y + dy))

    def is_mouse_over(self, mouse_pos):
        m_x, m_y = mouse_pos

        x_ok = self.x <= m_x <= self.x + self.w
        y_ok = self.y <= m_y <= self.y + self.h

        return x_ok and y_ok and not self.is_hidden and self.is_enabled

    def set_color(self, color):
        self.bg_color = color

    def hide(self):
        self.is_hidden = True

    def show(self):
        self.is_hidden = False

    def set_hidden(self, val):
        self.is_hidden = bool(val)

    def on_mouse_over(self):
        pass

    def on_mouse_out(self):
        pass

    def on_mouse_up(self):
        pass

    def get_mouse_up(self, mouse_pos):
        if self.is_mouse_over(mouse_pos):
            self.on_mouse_up()

    def get_mouse_over(self, mouse_pos):
        if self.is_mouse_over(mouse_pos):
            self.on_mouse_over()
        else:
            self.on_mouse_out()

    def set_enabled(self, on):
        self.is_enabled = on
        self.tint(on)

    def tint(self, on=True):
        self.is_tinted = on

    def set_img(self, img):
        self.img = pygame.transform.smoothscale(img, (self.w, self.h))

    def get_img(self):
        if self.is_hidden:
            surface = pygame.Surface((self.w, self.h))
            surface.set_alpha(0)
            return surface

        if isinstance(self.img, pygame.Surface):
            img = pygame.transform.smoothscale(self.img, (self.w, self.h))
        else:
            img = self.make_img()

        if self.is_tinted:
            img = tint(img, a=self.tint_alpha, color=self.tint_color)

        return img

    def render(self, target):
        img = self.get_img()
        if img is not None:
            target.blit(img, (self.x, self.y))

    def on_click(self):
        pass

    def get_click(self, mouse_pos):
        if self.is_mouse_over(mouse_pos):
            return self.on_click()


class UILabel(UIElement):
    def __init__(self, rect, text='', font_name=None, font_size=-1, antialias=True, font_color=BLACK,
                 img=None, bg_color=GRAY, frame_color=BLACK, frame_w=1,
                 text_align=(ALIGN_CENTER, ALIGN_CENTER)):
        super().__init__(rect, img, bg_color, frame_color, frame_w)

        if font_size <= 0:
            if text:
                font_size = min(((self.w - LABEL_TEXT_MARGIN * 2) // len(text)) * 2, self.h - LABEL_TEXT_MARGIN * 2)
            else:
                font_size = 0

        self.font = pygame.font.Font(font_name, font_size)
        self.font_name = font_name
        self.font_size = font_size
        self.text = text
        self.antialias = antialias
        self.font_color = font_color

        self.text_align = self.align_x, self.align_y = text_align

    def get_font(self):
        return self.font

    def set_alignment(self, alignment):
        self.text_align = self.align_x, self.align_y = alignment

    def get_alignment(self):
        return self.text_align

    def set_font(self, font_name, font_size):
        self.font = pygame.font.Font(font_name, font_size)
        self.font_name = font_name
        self.font_size = font_size

    def set_text(self, text, keep_font_size=False):
        if not keep_font_size:
            margin = self.frame_w + LABEL_TEXT_MARGIN
            font_size = min((self.w - margin) // len(text) * 2, self.h - margin)
            self.set_font(self.font_name, font_size)
        self.text = text

    def get_text_surface(self):
        text = self.get_font().render(self.text, self.antialias, self.font_color)
        return text

    def get_img(self):
        img = super(UILabel, self).get_img()
        text = self.get_text_surface()
        if isinstance(img, pygame.Surface):
            if self.text:
                margin = self.frame_w + LABEL_TEXT_MARGIN

                text_rect = text.get_rect()

                ax, ay = self.get_alignment()

                if ax == ALIGN_CENTER:
                    tx = (self.w - (text_rect.w + margin // 2)) // 2
                elif ax == ALIGN_LEFT:
                    tx = margin
                else:
                    tx = self.w - (text_rect.w + margin)

                if ay == ALIGN_CENTER:
                    ty = (self.h - (text_rect.h + margin // 2)) // 2
                elif ay == ALIGN_TOP:
                    ty = margin
                else:
                    ty = self.h - (text_rect.h + margin)

                img.blit(text, (tx, ty))
            return img
        return text


class UIButton(UILabel):
    def __init__(self, rect, action, img=None, text='', font_name=None, font_size=-1, antialias=True,
                 font_color=BLACK, bg_color=GRAY, frame_color=BLACK, frame_w=1,
                 text_align=(ALIGN_CENTER, ALIGN_CENTER)):
        super().__init__(rect, text=text, font_name=font_name, font_size=font_size,
                         antialias=antialias, font_color=font_color,
                         img=img, bg_color=bg_color, frame_color=frame_color, frame_w=frame_w,
                         text_align=text_align)
        self.action = action

    def on_mouse_out(self):
        self.is_tinted = False

    def on_mouse_up(self):
        self.tint_alpha = 50

    def on_mouse_over(self):
        self.tint_alpha = 50
        self.is_tinted = True

    def on_click(self):
        self.tint_alpha = 125
        if callable(self.action):
            self.action()


class UISlider(UIButton):
    def __init__(self, rect, min_value, max_value, action=None, do_draw_value=False, top=10, bottom=10,
                 bg_color=GRAY, frame_color=BLACK, handle_color=RED, scale_color=DARK_GRAY, scale_w=None):

        x, y, w, h = rect
        fsize = w // 2

        super().__init__(rect, action, text_align=(ALIGN_CENTER, ALIGN_TOP),
                         bg_color=bg_color, frame_color=frame_color, font_size=fsize)

        self.handle_color = handle_color
        self.scale_color = scale_color

        self.do_draw_value = do_draw_value

        self.top, self.bottom = top, bottom

        self.min_value, self.max_value = min_value, max_value
        self.value = min_value

        if do_draw_value:
            self.text = str(min_value)

        self.is_mouse_drag = False
        self.is_flipped = False

        if scale_w is None:
            scale_w = self.w // 4

        self.scale_w = scale_w

    def get_value(self):
        return self.value

    def get_scale_size(self):
        maxy = self.h - (self.frame_w + self.bottom)
        miny = self.frame_w + self.top

        if self.do_draw_value:
            miny += self.font_size

        return miny, maxy

    def get_handle_y(self):
        miny, maxy = self.get_scale_size()

        if not self.is_flipped:
            miny, maxy = maxy, miny

        if self.min_value == self.max_value == 0:
            return miny

        return map_value(self.value, self.min_value, self.max_value, miny, maxy)

    def get_img(self):
        img = super(UISlider, self).get_img()

        miny, maxy = self.get_scale_size()
        x = (self.w - self.scale_w) // 2

        pygame.draw.rect(img, self.scale_color, (x, miny, self.scale_w, (maxy - miny)), border_radius=5)
        pygame.draw.circle(img, self.handle_color, (x + self.scale_w // 2, self.get_handle_y()),
                           int(self.scale_w * 1.2))

        return img

    def set_constraints(self, minn, maxn):
        if minn > maxn:
            minn, maxn = maxn, minn

        self.max_value, self.min_value = maxn, minn
        self.set_value(constrain(self.value, minn, maxn))

    def set_value(self, value):
        self.value = constrain(value, self.min_value, self.max_value)

        if self.do_draw_value:
            self.text = str(value)

    def update_value(self, mouse_y):
        rel_y = mouse_y - self.y
        miny, maxy = self.get_scale_size()
        my = constrain(rel_y, miny, maxy)

        if not self.is_flipped:
            miny, maxy = maxy, miny

        new_value = int(map_value(my, miny, maxy, self.min_value, self.max_value))

        self.set_value(new_value)

    def on_click(self):
        if callable(self.action):
            self.action()
        self.is_mouse_drag = True

    def get_mouse_over(self, mouse_pos):
        super(UISlider, self).get_mouse_over(mouse_pos)
        if self.is_mouse_drag:
            _, my = mouse_pos
            self.update_value(my)

    def on_mouse_up(self):
        self.is_mouse_drag = False


class UISwitch(UIButton):
    def __init__(self, rect, action=None, on_img=None, off_img=None, text='', font_name=None, font_size=-1,
                 antialias=True, font_color=BLACK,
                 off_color=GRAY, on_color=BLUE, frame_color=BLACK, frame_w=1):
        super().__init__(rect, action, off_img, text, font_name, font_size, antialias, font_color,
                         off_color, frame_color, frame_w)
        self.state = False
        self.off_color = off_color
        self.on_color = on_color
        self.on_img = on_img
        self.off_img = off_img

    def on_click(self):
        self.state = not self.state
        if self.state:
            self.set_color(self.on_color)
            if self.on_img:
                self.set_img(self.on_img)
        else:
            self.set_color(self.off_color)
            if self.off_img:
                self.set_img(self.off_img)
        super(UISwitch, self).on_click()

    def get_state(self):
        return self.state


class UILcdDisplay(UILabel):
    def __init__(self, rect, text='', font_size=-1, font_color=BLACK, bg_color=LCD_BG_COLOR,
                 frame_color=BLACK, frame_w=1):
        super().__init__(rect, text, font_size=font_size, font_name=FONT_DS_PATH,
                         font_color=font_color, bg_color=bg_color, frame_color=frame_color,
                         frame_w=frame_w)


class UIGroup(UIElement):
    def __init__(self, rect, img=None, bg_color=GRAY, frame_color=BLACK, frame_w=1):
        super().__init__(rect, img, bg_color, frame_color, frame_w)
        self.elements = []

    def clear(self):
        for el in self.elements:
            del el
        self.elements = []

    def add_element(self, element):
        el_x, el_y = element.get_pos()
        element.set_pos((el_x + self.x, el_y + self.y))
        self.elements.append(element)

    def set_pos(self, pos):
        new_x, new_y = pos
        dx, dy = new_x - self.x, new_y - self.y

        for element in self.elements:
            el_x, el_y = element.get_pos()
            element.set_pos((el_x + dx, el_y + dy))

        self.x, self.y = pos

    def get_img(self):
        img = super(UIGroup, self).get_img()

        for el in self.elements:
            if check_intersection(self.get_rect(), el.get_rect()):
                el_img = el.get_img()
                if el_img is not None:
                    el_x, el_y = el.get_pos()
                    img.blit(el_img, (el_x - self.x, el_y - self.y))

        return img

    def get_click(self, mouse_pos):
        for el in self.elements:
            if el.is_mouse_over(mouse_pos):
                el.get_click(mouse_pos)
                return el

    def get_mouse_over(self, mouse_pos):
        for el in self.elements:
            el.get_mouse_over(mouse_pos)

    def get_mouse_up(self, mouse_pos):
        for el in self.elements:
            el.get_mouse_up(mouse_pos)


class UIListVertical(UIGroup):
    def __init__(self, rect, margin_top=0, margin_bottom=0, margin_side=0, separate_dist=0,
                 img=None, bg_color=GRAY, frame_color=BLACK, frame_w=1, slider_w=20, draw_slider=True):
        super().__init__(rect, img, bg_color, frame_color, frame_w)

        self.slider_w = self.old_slider_w = slider_w
        slider_rect = (self.x + self.w - self.slider_w, self.y, self.slider_w, self.h)
        self.y_offset_slider = UISlider(slider_rect, 0, 0, top=10, do_draw_value=False)
        self.y_offset_slider.is_flipped = True

        self.margin_side = margin_side
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom
        self.separate_dist = separate_dist

    def set_slider_hidden(self, on):
        self.y_offset_slider.set_hidden(on)
        self.slider_w = 0 if on else self.old_slider_w

    def set_pos(self, pos):
        new_x, new_y = pos
        dx, dy = new_x - self.x, new_y - self.y
        self.y_offset_slider.move(dx, dy)
        super(UIListVertical, self).set_pos(pos)

    def get_y_offset(self):
        return self.y_offset_slider.get_value()

    def get_above_h(self):
        out = 0
        for el in self.elements:
            out += (el.get_height() + self.separate_dist)
        return out

    def add_element(self, element, scale_to_fit=False):
        y_offset = self.get_above_h()
        element.set_pos((self.x + self.margin_side // 2, self.y + y_offset + self.margin_top))

        if scale_to_fit:
            w = self.w - (self.frame_w + self.margin_side + self.slider_w)
            h = element.get_height()
            element.set_size((w, h))

        self.elements.append(element)

        y_offset += (element.get_height() + self.separate_dist)
        self.y_offset_slider.set_constraints(0, y_offset)

        new_val = max(y_offset - self.h, 0)
        self.y_offset_slider.set_value(new_val)

    def get_img(self):
        img = super(UIGroup, self).get_img()

        for el in self.elements:

            el_x, el_y = el.get_pos()
            y_offset = self.get_y_offset()

            el_x, el_y = el_x - self.x, el_y - (self.y + y_offset)

            if el_y < self.y + self.h and el.x < self.x + self.h:
                el_img = el.get_img()
                if el_img is not None:
                    img.blit(el_img, (el_x, el_y))

        slider_img = self.y_offset_slider.get_img()
        img.blit(slider_img, (self.w - self.slider_w, 0))

        return img

    def get_click(self, mouse_pos):
        self.y_offset_slider.get_click(mouse_pos)

        mx, my = mouse_pos

        for el in self.elements:
            pos = mx, my + self.get_y_offset()
            el.get_click(pos)

    def get_mouse_over(self, mouse_pos):
        self.y_offset_slider.get_mouse_over(mouse_pos)

        mx, my = mouse_pos

        for el in self.elements:
            pos = mx, my + self.get_y_offset()
            el.get_mouse_over(pos)

    def get_mouse_up(self, mouse_pos):
        self.y_offset_slider.get_mouse_up(mouse_pos)

        mx, my = mouse_pos

        for el in self.elements:
            pos = mx, my + self.get_y_offset()
            el.get_mouse_up(pos)


def test():
    print('ok')


def main():
    size = 800, 800
    pygame.init()

    clock = pygame.time.Clock()

    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color('white'))

    lcd = UILcdDisplay((10, 10, 150, 50), '02:00', frame_w=1)
    lcd2 = UILcdDisplay((10, 10, 300, 50), '02:00', frame_w=1)
    btn = UIButton((10, 110, 200, 50), test, text='press me', frame_w=5)
    btn2 = UIButton((10, 110, 150, 50), test, text='press me2', frame_w=5)
    switch = UISwitch((10, 210, 200, 50))
    slider = UISlider((500, 10, 20, 210), 0, 10, top=10, do_draw_value=True)
    slider.is_flipped = True
    group = UIGroup((100, 0, 220, 300))

    v_list = UIListVertical((100, 350, 220, 400), margin_side=10, margin_top=10, separate_dist=20)

    group.add_element(lcd)
    group.add_element(btn)
    group.add_element(switch)

    v_list.add_element(lcd2, True)
    v_list.add_element(btn2)

    group.render(screen)
    slider.render(screen)
    v_list.render(screen)
    pygame.display.flip()

    mpos = pygame.mouse.get_pos()

    running = True
    while running:
        has_interacted = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                group.get_click(mpos)
                slider.get_click(mpos)
                v_list.get_click(mpos)
                has_interacted = True
            if event.type == pygame.MOUSEBUTTONUP:
                group.get_mouse_up(mpos)
                slider.get_mouse_up(mpos)
                v_list.get_mouse_up(mpos)
                has_interacted = True
            if event.type == pygame.MOUSEMOTION:
                mpos = pygame.mouse.get_pos()
                slider.get_mouse_over(mpos)
                v_list.get_mouse_over(mpos)
                group.get_mouse_over(mpos)
                has_interacted = True

        if has_interacted:
            screen.fill(pygame.Color('white'))
            group.render(screen)
            slider.render(screen)
            v_list.render(screen)
            pygame.display.flip()

        clock.tick(30)
    pygame.quit()


if __name__ == '__main__':
    main()
