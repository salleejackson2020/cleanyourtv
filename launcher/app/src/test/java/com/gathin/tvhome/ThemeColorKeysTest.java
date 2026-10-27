package com.gathin.tvhome;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

/** The colour keys (dock_band_color, pill_color, header_color, hero_color, tile_name_color): "#RRGGBB" or off. */
public class ThemeColorKeysTest {

    @Test
    public void hexBecomesAnOpaqueColour() {
        assertEquals(0xFF3D1657, Config.themeColor("#3D1657"));
        assertEquals(0xFFC4561C, Config.themeColor(" #c4561c "));
    }

    @Test
    public void emptyIsOff() {
        assertEquals(0, Config.themeColor(""));
        assertEquals(0, Config.themeColor("   "));
        assertEquals(0, Config.themeColor(null));
    }

    @Test
    public void anythingElseIsOff() {
        assertEquals(0, Config.themeColor("orange"));
        assertEquals(0, Config.themeColor("#FFF"));
        assertEquals(0, Config.themeColor("#80C4561C"));
        assertEquals(0, Config.themeColor("C4561C"));
    }
}
