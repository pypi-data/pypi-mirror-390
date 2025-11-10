use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::collections::HashMap;
use std::thread;
use std::time::Duration;

// Color constants
#[pyclass]
struct ColoredText;

#[pymethods]
impl ColoredText {
    // Foreground colors
    #[classattr]
    const BLACK: i32 = 30;
    #[classattr]
    const RED: i32 = 31;
    #[classattr]
    const GREEN: i32 = 32;
    #[classattr]
    const YELLOW: i32 = 33;
    #[classattr]
    const BLUE: i32 = 34;
    #[classattr]
    const MAGENTA: i32 = 35;
    #[classattr]
    const CYAN: i32 = 36;
    #[classattr]
    const WHITE: i32 = 37;
    
    // Bright foreground colors
    #[classattr]
    const BRIGHT_BLACK: i32 = 90;
    #[classattr]
    const BRIGHT_RED: i32 = 91;
    #[classattr]
    const BRIGHT_GREEN: i32 = 92;
    #[classattr]
    const BRIGHT_YELLOW: i32 = 93;
    #[classattr]
    const BRIGHT_BLUE: i32 = 94;
    #[classattr]
    const BRIGHT_MAGENTA: i32 = 95;
    #[classattr]
    const BRIGHT_CYAN: i32 = 96;
    #[classattr]
    const BRIGHT_WHITE: i32 = 97;
    
    // Background colors
    #[classattr]
    const BG_BLACK: i32 = 40;
    #[classattr]
    const BG_RED: i32 = 41;
    #[classattr]
    const BG_GREEN: i32 = 42;
    #[classattr]
    const BG_YELLOW: i32 = 43;
    #[classattr]
    const BG_BLUE: i32 = 44;
    #[classattr]
    const BG_MAGENTA: i32 = 45;
    #[classattr]
    const BG_CYAN: i32 = 46;
    #[classattr]
    const BG_WHITE: i32 = 47;
    
    // Bright background colors
    #[classattr]
    const BG_BRIGHT_BLACK: i32 = 100;
    #[classattr]
    const BG_BRIGHT_RED: i32 = 101;
    #[classattr]
    const BG_BRIGHT_GREEN: i32 = 102;
    #[classattr]
    const BG_BRIGHT_YELLOW: i32 = 103;
    #[classattr]
    const BG_BRIGHT_BLUE: i32 = 104;
    #[classattr]
    const BG_BRIGHT_MAGENTA: i32 = 105;
    #[classattr]
    const BG_BRIGHT_CYAN: i32 = 106;
    #[classattr]
    const BG_BRIGHT_WHITE: i32 = 107;
    
    // Styles
    #[classattr]
    const BOLD: i32 = 1;
    #[classattr]
    const DIM: i32 = 2;
    #[classattr]
    const ITALIC: i32 = 3;
    #[classattr]
    const UNDERLINE: i32 = 4;
    #[classattr]
    const BLINK: i32 = 5;
    #[classattr]
    const RAPID_BLINK: i32 = 6;
    #[classattr]
    const REVERSE: i32 = 7;
    #[classattr]
    const HIDDEN: i32 = 8;
    #[classattr]
    const STRIKETHROUGH: i32 = 9;
    #[classattr]
    const RESET: i32 = 0;
    
    #[staticmethod]
    fn colorize(text: &str, fg_color: Option<i32>, bg_color: Option<i32>, style: Option<i32>) -> String {
        let mut codes = Vec::new();
        
        if let Some(s) = style {
            codes.push(s.to_string());
        }
        if let Some(fg) = fg_color {
            codes.push(fg.to_string());
        }
        if let Some(bg) = bg_color {
            codes.push(bg.to_string());
        }
        
        if codes.is_empty() {
            return text.to_string();
        }
        
        format!("\x1b[{}m{}\x1b[0m", codes.join(";"), text)
    }
    
    #[staticmethod]
    fn rgb(text: &str, r: u8, g: u8, b: u8, bg: Option<bool>, style: Option<i32>) -> String {
        let mut codes = Vec::new();
        
        if let Some(s) = style {
            codes.push(s.to_string());
        }
        
        if bg.unwrap_or(false) {
            codes.push(format!("48;2;{};{};{}", r, g, b));
        } else {
            codes.push(format!("38;2;{};{};{}", r, g, b));
        }
        
        format!("\x1b[{}m{}\x1b[0m", codes.join(";"), text)
    }
    
    #[staticmethod]
    fn rgb_bg(text: &str, r: u8, g: u8, b: u8, fg_r: Option<u8>, fg_g: Option<u8>, fg_b: Option<u8>, style: Option<i32>) -> String {
        let mut codes = Vec::new();
        
        if let Some(s) = style {
            codes.push(s.to_string());
        }
        
        if let (Some(fr), Some(fg), Some(fb)) = (fg_r, fg_g, fg_b) {
            codes.push(format!("38;2;{};{};{}", fr, fg, fb));
        }
        
        codes.push(format!("48;2;{};{};{}", r, g, b));
        
        format!("\x1b[{}m{}\x1b[0m", codes.join(";"), text)
    }
    
    #[staticmethod]
    fn hex_color(text: &str, hex_code: &str, bg: Option<bool>, style: Option<i32>) -> PyResult<String> {
        let hex = hex_code.trim_start_matches('#');
        
        let hex_expanded = if hex.len() == 3 {
            hex.chars()
                .map(|c| format!("{}{}", c, c))
                .collect::<String>()
        } else {
            hex.to_string()
        };
        
        if hex_expanded.len() != 6 {
            return Err(PyValueError::new_err("Invalid hex code. Expected format: #RRGGBB"));
        }
        
        let r = u8::from_str_radix(&hex_expanded[0..2], 16)
            .map_err(|_| PyValueError::new_err("Invalid hex code"))?;
        let g = u8::from_str_radix(&hex_expanded[2..4], 16)
            .map_err(|_| PyValueError::new_err("Invalid hex code"))?;
        let b = u8::from_str_radix(&hex_expanded[4..6], 16)
            .map_err(|_| PyValueError::new_err("Invalid hex code"))?;
        
        Ok(Self::rgb(text, r, g, b, bg, style))
    }
    
    #[staticmethod]
    fn gradient_text(text: &str, start_rgb: (u8, u8, u8), end_rgb: (u8, u8, u8), style: Option<i32>) -> String {
        let (start_r, start_g, start_b) = start_rgb;
        let (end_r, end_g, end_b) = end_rgb;
        
        let chars: Vec<char> = text.chars().collect();
        let len = chars.len().saturating_sub(1).max(1) as f32;
        
        chars.iter().enumerate()
            .map(|(i, &ch)| {
                if ch.is_whitespace() {
                    ch.to_string()
                } else {
                    let ratio = i as f32 / len;
                    let r = (start_r as f32 + (end_r as i16 - start_r as i16) as f32 * ratio) as u8;
                    let g = (start_g as f32 + (end_g as i16 - start_g as i16) as f32 * ratio) as u8;
                    let b = (start_b as f32 + (end_b as i16 - start_b as i16) as f32 * ratio) as u8;
                    Self::rgb(&ch.to_string(), r, g, b, None, style)
                }
            })
            .collect()
    }
    
    #[staticmethod]
    fn rainbow(text: &str, style: Option<i32>) -> String {
        let colors = vec![
            (255, 0, 0), (255, 127, 0), (255, 255, 0),
            (0, 255, 0), (0, 0, 255), (75, 0, 130), (143, 0, 255)
        ];
        
        text.chars()
            .enumerate()
            .map(|(i, ch)| {
                if ch.is_whitespace() {
                    ch.to_string()
                } else {
                    let (r, g, b) = colors[i % colors.len()];
                    Self::rgb(&ch.to_string(), r, g, b, None, style)
                }
            })
            .collect()
    }
    
    #[staticmethod]
    fn progress_bar(
        progress: f32,
        width: Option<usize>,
        fill_char: Option<&str>,
        empty_char: Option<&str>,
        start_char: Option<&str>,
        end_char: Option<&str>,
        show_percentage: Option<bool>,
        bar_color: Option<(u8, u8, u8)>
    ) -> String {
        let progress = progress.max(0.0).min(1.0);
        let width = width.unwrap_or(50);
        let fill_char = fill_char.unwrap_or("█");
        let empty_char = empty_char.unwrap_or("░");
        let start_char = start_char.unwrap_or("|");
        let end_char = end_char.unwrap_or("|");
        let show_percentage = show_percentage.unwrap_or(true);
        
        let filled_width = (width as f32 * progress) as usize;
        let empty_width = width - filled_width;
        
        let mut filled_part = fill_char.repeat(filled_width);
        if let Some((r, g, b)) = bar_color {
            filled_part = Self::rgb(&filled_part, r, g, b, None, None);
        }
        
        let empty_part = empty_char.repeat(empty_width);
        let mut bar = format!("{}{}{}{}", start_char, filled_part, empty_part, end_char);
        
        if show_percentage {
            bar.push_str(&format!(" {}%", (progress * 100.0) as i32));
        }
        
        bar
    }
    
    #[staticmethod]
    fn table(
        data: Vec<Vec<String>>,
        headers: Option<Vec<String>>,
        padding: Option<usize>,
        border_style: Option<&str>,
        align: Option<&str>
    ) -> String {
        let padding = padding.unwrap_or(1);
        let border_style = border_style.unwrap_or("single");
        let align = align.unwrap_or("left");
        
        let borders = get_border_chars(border_style);
        
        let mut all_rows = Vec::new();
        if let Some(ref h) = headers {
            all_rows.push(h.clone());
        }
        all_rows.extend(data.clone());
        
        if all_rows.is_empty() || all_rows[0].is_empty() {
            return String::new();
        }
        
        let col_count = all_rows[0].len();
        let mut col_widths = vec![0; col_count];
        
        for row in &all_rows {
            for (i, cell) in row.iter().enumerate().take(col_count) {
                col_widths[i] = col_widths[i].max(cell.len());
            }
        }
        
        let mut result = Vec::new();
        
        // Top border
        result.push(create_separator(&borders, &col_widths, padding, "top"));
        
        // Headers
        if let Some(ref h) = headers {
            result.push(create_row(&borders, h, &col_widths, padding, align));
            result.push(create_separator(&borders, &col_widths, padding, "middle"));
        }
        
        // Data rows
        for row in &data {
            result.push(create_row(&borders, row, &col_widths, padding, align));
        }
        
        // Bottom border
        result.push(create_separator(&borders, &col_widths, padding, "bottom"));
        
        result.join("\n")
    }
    
    #[staticmethod]
    fn hsl_to_rgb(h: f32, s: f32, l: f32) -> (u8, u8, u8) {
        let h = h % 360.0;
        let s = s.max(0.0).min(1.0);
        let l = l.max(0.0).min(1.0);
        
        if s == 0.0 {
            let val = (l * 255.0) as u8;
            return (val, val, val);
        }
        
        let q = if l < 0.5 { l * (1.0 + s) } else { l + s - l * s };
        let p = 2.0 * l - q;
        
        let hue_to_rgb = |p: f32, q: f32, mut t: f32| -> f32 {
            if t < 0.0 { t += 1.0; }
            if t > 1.0 { t -= 1.0; }
            if t < 1.0/6.0 { return p + (q - p) * 6.0 * t; }
            if t < 1.0/2.0 { return q; }
            if t < 2.0/3.0 { return p + (q - p) * (2.0/3.0 - t) * 6.0; }
            p
        };
        
        let h_norm = h / 360.0;
        let r = (hue_to_rgb(p, q, h_norm + 1.0/3.0) * 255.0) as u8;
        let g = (hue_to_rgb(p, q, h_norm) * 255.0) as u8;
        let b = (hue_to_rgb(p, q, h_norm - 1.0/3.0) * 255.0) as u8;
        
        (r, g, b)
    }
    
    #[staticmethod]
    fn hsl(text: &str, h: f32, s: f32, l: f32, bg: Option<bool>, style: Option<i32>) -> String {
        let (r, g, b) = Self::hsl_to_rgb(h, s, l);
        Self::rgb(text, r, g, b, bg, style)
    }
}

struct BorderChars {
    tl: &'static str, t: &'static str, tr: &'static str,
    l: &'static str, r: &'static str,
    ml: &'static str, m: &'static str, mr: &'static str,
    bl: &'static str, b: &'static str, br: &'static str,
    c: &'static str,
}

fn get_border_chars(style: &str) -> BorderChars {
    match style {
        "double" => BorderChars {
            tl: "╔", t: "═", tr: "╗",
            l: "║", r: "║",
            ml: "╠", m: "═", mr: "╣",
            bl: "╚", b: "═", br: "╝",
            c: "╬",
        },
        "rounded" => BorderChars {
            tl: "╭", t: "─", tr: "╮",
            l: "│", r: "│",
            ml: "├", m: "─", mr: "┤",
            bl: "╰", b: "─", br: "╯",
            c: "┼",
        },
        "bold" => BorderChars {
            tl: "┏", t: "━", tr: "┓",
            l: "┃", r: "┃",
            ml: "┣", m: "━", mr: "┫",
            bl: "┗", b: "━", br: "┛",
            c: "╋",
        },
        _ => BorderChars { // single
            tl: "┌", t: "─", tr: "┐",
            l: "│", r: "│",
            ml: "├", m: "─", mr: "┤",
            bl: "└", b: "─", br: "┘",
            c: "┼",
        },
    }
}

fn create_separator(borders: &BorderChars, col_widths: &[usize], padding: usize, position: &str) -> String {
    let (left, mid, right, fill) = match position {
        "top" => (borders.tl, borders.t, borders.tr, borders.t),
        "middle" => (borders.ml, borders.m, borders.mr, borders.m),
        _ => (borders.bl, borders.b, borders.br, borders.b),
    };
    
    let segments: Vec<String> = col_widths.iter()
        .map(|&w| fill.repeat(w + padding * 2))
        .collect();
    
    format!("{}{}{}", left, segments.join(mid), right)
}

fn create_row(borders: &BorderChars, row: &[String], col_widths: &[usize], padding: usize, align: &str) -> String {
    let cells: Vec<String> = row.iter()
        .zip(col_widths.iter())
        .map(|(cell, &width)| {
            let formatted = match align {
                "right" => format!("{:>width$}", cell, width = width),
                "center" => format!("{:^width$}", cell, width = width),
                _ => format!("{:<width$}", cell, width = width),
            };
            format!("{}{}{}", " ".repeat(padding), formatted, " ".repeat(padding))
        })
        .collect();
    
    format!("{}{}{}", borders.l, cells.join(borders.l), borders.r)
}

#[pymodule]
fn chromin(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<ColoredText>()?;
    Ok(())
}
