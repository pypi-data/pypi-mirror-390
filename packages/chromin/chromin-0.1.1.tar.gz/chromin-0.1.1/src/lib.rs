use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::collections::HashMap;
use std::thread;
use std::time::Duration;
use std::io::{self, Write};

// Color constants
const BLACK: u8 = 30;
const RED: u8 = 31;
const GREEN: u8 = 32;
const YELLOW: u8 = 33;
const BLUE: u8 = 34;
const MAGENTA: u8 = 35;
const CYAN: u8 = 36;
const WHITE: u8 = 37;

const BRIGHT_BLACK: u8 = 90;
const BRIGHT_RED: u8 = 91;
const BRIGHT_GREEN: u8 = 92;
const BRIGHT_YELLOW: u8 = 93;
const BRIGHT_BLUE: u8 = 94;
const BRIGHT_MAGENTA: u8 = 95;
const BRIGHT_CYAN: u8 = 96;
const BRIGHT_WHITE: u8 = 97;

// Background colors
const BG_BLACK: u8 = 40;
const BG_RED: u8 = 41;
const BG_GREEN: u8 = 42;
const BG_YELLOW: u8 = 43;
const BG_BLUE: u8 = 44;
const BG_MAGENTA: u8 = 45;
const BG_CYAN: u8 = 46;
const BG_WHITE: u8 = 47;

const BG_BRIGHT_BLACK: u8 = 100;
const BG_BRIGHT_RED: u8 = 101;
const BG_BRIGHT_GREEN: u8 = 102;
const BG_BRIGHT_YELLOW: u8 = 103;
const BG_BRIGHT_BLUE: u8 = 104;
const BG_BRIGHT_MAGENTA: u8 = 105;
const BG_BRIGHT_CYAN: u8 = 106;
const BG_BRIGHT_WHITE: u8 = 107;

// Styles
const BOLD: u8 = 1;
const DIM: u8 = 2;
const ITALIC: u8 = 3;
const UNDERLINE: u8 = 4;
const BLINK: u8 = 5;
const RAPID_BLINK: u8 = 6;
const REVERSE: u8 = 7;
const HIDDEN: u8 = 8;
const STRIKETHROUGH: u8 = 9;
const RESET: u8 = 0;

#[pyclass]
struct ColoredText;

#[pymethods]
impl ColoredText {
    #[new]
    fn new() -> Self {
        ColoredText
    }

    // Constants as class attributes
    #[classattr]
    const BLACK: u8 = BLACK;
    #[classattr]
    const RED: u8 = RED;
    #[classattr]
    const GREEN: u8 = GREEN;
    #[classattr]
    const YELLOW: u8 = YELLOW;
    #[classattr]
    const BLUE: u8 = BLUE;
    #[classattr]
    const MAGENTA: u8 = MAGENTA;
    #[classattr]
    const CYAN: u8 = CYAN;
    #[classattr]
    const WHITE: u8 = WHITE;
    
    #[classattr]
    const BRIGHT_BLACK: u8 = BRIGHT_BLACK;
    #[classattr]
    const BRIGHT_RED: u8 = BRIGHT_RED;
    #[classattr]
    const BRIGHT_GREEN: u8 = BRIGHT_GREEN;
    #[classattr]
    const BRIGHT_YELLOW: u8 = BRIGHT_YELLOW;
    #[classattr]
    const BRIGHT_BLUE: u8 = BRIGHT_BLUE;
    #[classattr]
    const BRIGHT_MAGENTA: u8 = BRIGHT_MAGENTA;
    #[classattr]
    const BRIGHT_CYAN: u8 = BRIGHT_CYAN;
    #[classattr]
    const BRIGHT_WHITE: u8 = BRIGHT_WHITE;
    
    #[classattr]
    const BG_BLACK: u8 = BG_BLACK;
    #[classattr]
    const BG_RED: u8 = BG_RED;
    #[classattr]
    const BG_GREEN: u8 = BG_GREEN;
    #[classattr]
    const BG_YELLOW: u8 = BG_YELLOW;
    #[classattr]
    const BG_BLUE: u8 = BG_BLUE;
    #[classattr]
    const BG_MAGENTA: u8 = BG_MAGENTA;
    #[classattr]
    const BG_CYAN: u8 = BG_CYAN;
    #[classattr]
    const BG_WHITE: u8 = BG_WHITE;
    
    #[classattr]
    const BG_BRIGHT_BLACK: u8 = BG_BRIGHT_BLACK;
    #[classattr]
    const BG_BRIGHT_RED: u8 = BG_BRIGHT_RED;
    #[classattr]
    const BG_BRIGHT_GREEN: u8 = BG_BRIGHT_GREEN;
    #[classattr]
    const BG_BRIGHT_YELLOW: u8 = BG_BRIGHT_YELLOW;
    #[classattr]
    const BG_BRIGHT_BLUE: u8 = BG_BRIGHT_BLUE;
    #[classattr]
    const BG_BRIGHT_MAGENTA: u8 = BG_BRIGHT_MAGENTA;
    #[classattr]
    const BG_BRIGHT_CYAN: u8 = BG_BRIGHT_CYAN;
    #[classattr]
    const BG_BRIGHT_WHITE: u8 = BG_BRIGHT_WHITE;
    
    #[classattr]
    const BOLD: u8 = BOLD;
    #[classattr]
    const DIM: u8 = DIM;
    #[classattr]
    const ITALIC: u8 = ITALIC;
    #[classattr]
    const UNDERLINE: u8 = UNDERLINE;
    #[classattr]
    const BLINK: u8 = BLINK;
    #[classattr]
    const RAPID_BLINK: u8 = RAPID_BLINK;
    #[classattr]
    const REVERSE: u8 = REVERSE;
    #[classattr]
    const HIDDEN: u8 = HIDDEN;
    #[classattr]
    const STRIKETHROUGH: u8 = STRIKETHROUGH;
    #[classattr]
    const RESET: u8 = RESET;

    #[staticmethod]
    fn colorize(text: &str, fg_color: Option<u8>, bg_color: Option<u8>, style: Option<u8>) -> String {
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
    fn print_colored(text: &str, fg_color: Option<u8>, bg_color: Option<u8>, style: Option<u8>) {
        println!("{}", Self::colorize(text, fg_color, bg_color, style));
    }

    #[staticmethod]
    fn color256(text: &str, color_code: u8, bg_code: Option<u8>, style: Option<u8>) -> String {
        let mut codes = Vec::new();
        
        if let Some(s) = style {
            codes.push(s.to_string());
        }
        codes.push(format!("38;5;{}", color_code));
        if let Some(bg) = bg_code {
            codes.push(format!("48;5;{}", bg));
        }
        
        format!("\x1b[{}m{}\x1b[0m", codes.join(";"), text)
    }

    #[staticmethod]
    fn rgb(text: &str, r: u8, g: u8, b: u8, bg: Option<bool>, style: Option<u8>) -> String {
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
    fn rgb_bg(
        text: &str,
        r: u8,
        g: u8,
        b: u8,
        fg_r: Option<u8>,
        fg_g: Option<u8>,
        fg_b: Option<u8>,
        style: Option<u8>,
    ) -> String {
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
    fn hex_color(text: &str, hex_code: &str, bg: Option<bool>, style: Option<u8>) -> PyResult<String> {
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
    fn hex_bg(
        text: &str,
        hex_code: &str,
        fg_hex: Option<&str>,
        style: Option<u8>,
    ) -> PyResult<String> {
        let parse_hex = |hex: &str| -> PyResult<(u8, u8, u8)> {
            let hex = hex.trim_start_matches('#');
            let hex_expanded = if hex.len() == 3 {
                hex.chars()
                    .map(|c| format!("{}{}", c, c))
                    .collect::<String>()
            } else {
                hex.to_string()
            };
            
            if hex_expanded.len() != 6 {
                return Err(PyValueError::new_err("Invalid hex code"));
            }
            
            let r = u8::from_str_radix(&hex_expanded[0..2], 16)?;
            let g = u8::from_str_radix(&hex_expanded[2..4], 16)?;
            let b = u8::from_str_radix(&hex_expanded[4..6], 16)?;
            
            Ok((r, g, b))
        };
        
        let (bg_r, bg_g, bg_b) = parse_hex(hex_code)?;
        
        let (fg_r, fg_g, fg_b) = if let Some(fg) = fg_hex {
            let (r, g, b) = parse_hex(fg)?;
            (Some(r), Some(g), Some(b))
        } else {
            (None, None, None)
        };
        
        Ok(Self::rgb_bg(text, bg_r, bg_g, bg_b, fg_r, fg_g, fg_b, style))
    }

    #[staticmethod]
    fn hsl_to_rgb(h: f64, s: f64, l: f64) -> (u8, u8, u8) {
        let h = h % 360.0;
        let s = s.max(0.0).min(1.0);
        let l = l.max(0.0).min(1.0);
        
        if s == 0.0 {
            let gray = (l * 255.0) as u8;
            return (gray, gray, gray);
        }
        
        let hue_to_rgb = |p: f64, q: f64, mut t: f64| -> f64 {
            if t < 0.0 {
                t += 1.0;
            }
            if t > 1.0 {
                t -= 1.0;
            }
            if t < 1.0 / 6.0 {
                return p + (q - p) * 6.0 * t;
            }
            if t < 1.0 / 2.0 {
                return q;
            }
            if t < 2.0 / 3.0 {
                return p + (q - p) * (2.0 / 3.0 - t) * 6.0;
            }
            p
        };
        
        let q = if l < 0.5 {
            l * (1.0 + s)
        } else {
            l + s - l * s
        };
        let p = 2.0 * l - q;
        
        let r = (hue_to_rgb(p, q, h / 360.0 + 1.0 / 3.0) * 255.0) as u8;
        let g = (hue_to_rgb(p, q, h / 360.0) * 255.0) as u8;
        let b = (hue_to_rgb(p, q, h / 360.0 - 1.0 / 3.0) * 255.0) as u8;
        
        (r, g, b)
    }

    #[staticmethod]
    fn hsl(text: &str, h: f64, s: f64, l: f64, bg: Option<bool>, style: Option<u8>) -> String {
        let (r, g, b) = Self::hsl_to_rgb(h, s, l);
        Self::rgb(text, r, g, b, bg, style)
    }

    #[staticmethod]
    fn hsl_bg(
        text: &str,
        h: f64,
        s: f64,
        l: f64,
        fg_h: Option<f64>,
        fg_s: Option<f64>,
        fg_l: Option<f64>,
        style: Option<u8>,
    ) -> String {
        let (bg_r, bg_g, bg_b) = Self::hsl_to_rgb(h, s, l);
        
        let (fg_r, fg_g, fg_b) = if let (Some(fh), Some(fs), Some(fl)) = (fg_h, fg_s, fg_l) {
            let (r, g, b) = Self::hsl_to_rgb(fh, fs, fl);
            (Some(r), Some(g), Some(b))
        } else {
            (None, None, None)
        };
        
        Self::rgb_bg(text, bg_r, bg_g, bg_b, fg_r, fg_g, fg_b, style)
    }

    #[staticmethod]
    fn from_preset(text: &str, preset_name: &str, style: Option<u8>) -> PyResult<String> {
        let presets = get_color_presets();
        
        let (r, g, b) = presets.get(preset_name).ok_or_else(|| {
            let available: Vec<&str> = presets.keys().map(|s| s.as_str()).collect();
            PyValueError::new_err(format!(
                "Unknown preset '{}'. Available presets: {}",
                preset_name,
                available.join(", ")
            ))
        })?;
        
        Ok(Self::rgb(text, *r, *g, *b, None, style))
    }

    #[staticmethod]
    fn from_theme(text: &str, theme_name: &str) -> PyResult<String> {
        let themes = get_theme_presets();
        
        let theme = themes.get(theme_name).ok_or_else(|| {
            let available: Vec<&str> = themes.keys().map(|s| s.as_str()).collect();
            PyValueError::new_err(format!(
                "Unknown theme '{}'. Available themes: {}",
                theme_name,
                available.join(", ")
            ))
        })?;
        
        Ok(Self::rgb_bg(
            text,
            theme.bg.0,
            theme.bg.1,
            theme.bg.2,
            Some(theme.fg.0),
            Some(theme.fg.1),
            Some(theme.fg.2),
            theme.style,
        ))
    }

    #[staticmethod]
    fn gradient_text(text: &str, start_rgb: (u8, u8, u8), end_rgb: (u8, u8, u8), style: Option<u8>) -> String {
        let chars: Vec<char> = text.chars().collect();
        let len = chars.len();
        
        if len <= 1 {
            return Self::rgb(text, start_rgb.0, start_rgb.1, start_rgb.2, None, style);
        }
        
        let mut result = String::new();
        
        for (i, ch) in chars.iter().enumerate() {
            if ch.is_whitespace() {
                result.push(*ch);
                continue;
            }
            
            let ratio = i as f64 / (len - 1) as f64;
            let r = (start_rgb.0 as f64 + (end_rgb.0 as i16 - start_rgb.0 as i16) as f64 * ratio) as u8;
            let g = (start_rgb.1 as f64 + (end_rgb.1 as i16 - start_rgb.1 as i16) as f64 * ratio) as u8;
            let b = (start_rgb.2 as f64 + (end_rgb.2 as i16 - start_rgb.2 as i16) as f64 * ratio) as u8;
            
            result.push_str(&Self::rgb(&ch.to_string(), r, g, b, None, style));
        }
        
        result
    }

    #[staticmethod]
    fn rainbow(text: &str, style: Option<u8>) -> String {
        let colors = vec![
            (255, 0, 0),
            (255, 127, 0),
            (255, 255, 0),
            (0, 255, 0),
            (0, 0, 255),
            (75, 0, 130),
            (143, 0, 255),
        ];
        
        let mut result = String::new();
        let mut color_idx = 0;
        
        for ch in text.chars() {
            if ch.is_whitespace() {
                result.push(ch);
                continue;
            }
            
            let (r, g, b) = colors[color_idx % colors.len()];
            result.push_str(&Self::rgb(&ch.to_string(), r, g, b, None, style));
            color_idx += 1;
        }
        
        result
    }

    #[staticmethod]
    fn progress_bar(
        progress: f64,
        width: Option<usize>,
        fill_char: Option<&str>,
        empty_char: Option<&str>,
        start_char: Option<&str>,
        end_char: Option<&str>,
        show_percentage: Option<bool>,
        bar_color: Option<(u8, u8, u8)>,
        percentage_color: Option<(u8, u8, u8)>,
    ) -> String {
        let progress = progress.max(0.0).min(1.0);
        let width = width.unwrap_or(50);
        let fill_char = fill_char.unwrap_or("█");
        let empty_char = empty_char.unwrap_or("░");
        let start_char = start_char.unwrap_or("|");
        let end_char = end_char.unwrap_or("|");
        let show_percentage = show_percentage.unwrap_or(true);
        
        let filled_width = (width as f64 * progress) as usize;
        let empty_width = width - filled_width;
        
        let mut filled_part = fill_char.repeat(filled_width);
        let empty_part = empty_char.repeat(empty_width);
        
        if let Some((r, g, b)) = bar_color {
            filled_part = Self::rgb(&filled_part, r, g, b, None, None);
        }
        
        let mut bar = format!("{}{}{}{}", start_char, filled_part, empty_part, end_char);
        
        if show_percentage {
            let mut percentage = format!(" {}%", (progress * 100.0) as i32);
            if let Some((r, g, b)) = percentage_color {
                percentage = Self::rgb(&percentage, r, g, b, None, None);
            }
            bar.push_str(&percentage);
        }
        
        bar
    }

    #[staticmethod]
    fn table(
        data: Vec<Vec<String>>,
        headers: Option<Vec<String>>,
        padding: Option<usize>,
        border_style: Option<&str>,
        header_color: Option<(u8, u8, u8)>,
        align: Option<&str>,
    ) -> String {
        let padding = padding.unwrap_or(1);
        let border_style = border_style.unwrap_or("single");
        let align = align.unwrap_or("left");
        
        let borders = get_border_chars(border_style);
        
        let mut all_rows = Vec::new();
        if let Some(h) = headers.as_ref() {
            all_rows.push(h.clone());
        }
        all_rows.extend(data.clone());
        
        if all_rows.is_empty() {
            return String::new();
        }
        
        let num_cols = all_rows[0].len();
        let mut col_widths = vec![0; num_cols];
        
        for row in &all_rows {
            for (i, cell) in row.iter().enumerate() {
                col_widths[i] = col_widths[i].max(cell.len());
            }
        }
        
        let format_cell = |content: &str, width: usize, alignment: &str| -> String {
            match alignment {
                "right" => format!("{:>width$}", content, width = width),
                "center" => format!("{:^width$}", content, width = width),
                _ => format!("{:<width$}", content, width = width),
            }
        };
        
        let create_separator = |left: &str, mid: &str, right: &str, fill: &str| -> String {
            let parts: Vec<String> = col_widths
                .iter()
                .map(|w| fill.repeat(w + padding * 2))
                .collect();
            format!("{}{}{}", left, parts.join(mid), right)
        };
        
        let mut result = Vec::new();
        result.push(create_separator(&borders.tl, &borders.t, &borders.tr, &borders.t));
        
        let mut data_start_idx = 0;
        if let Some(h) = headers.as_ref() {
            let mut header_row = borders.l.to_string();
            for (i, (header, width)) in h.iter().zip(&col_widths).enumerate() {
                let mut cell = format!(
                    "{}{}{}",
                    " ".repeat(padding),
                    format_cell(header, *width, align),
                    " ".repeat(padding)
                );
                
                if let Some((r, g, b)) = header_color {
                    cell = Self::rgb(&cell, r, g, b, None, None);
                }
                
                header_row.push_str(&cell);
                header_row.push_str(&borders.l);
            }
            result.push(header_row);
            result.push(create_separator(&borders.ml, &borders.m, &borders.mr, &borders.m));
            data_start_idx = 1;
        }
        
        for row in &all_rows[data_start_idx..] {
            let mut row_str = borders.l.to_string();
            for (cell, width) in row.iter().zip(&col_widths) {
                let cell_content = format!(
                    "{}{}{}",
                    " ".repeat(padding),
                    format_cell(cell, *width, align),
                    " ".repeat(padding)
                );
                row_str.push_str(&cell_content);
                row_str.push_str(&borders.l);
            }
            result.push(row_str);
        }
        
        result.push(create_separator(&borders.bl, &borders.b, &borders.br, &borders.b));
        
        result.join("\n")
    }

    #[staticmethod]
    fn box_text(
        text: &str,
        padding: Option<usize>,
        border_style: Option<&str>,
        fg_color: Option<u8>,
        bg_color: Option<u8>,
        style: Option<u8>,
    ) -> String {
        let padding = padding.unwrap_or(1);
        let border_style = border_style.unwrap_or("single");
        
        let lines: Vec<&str> = text.lines().collect();
        let width = lines.iter().map(|l| l.len()).max().unwrap_or(0);
        
        let borders = get_border_chars(border_style);
        
        let horizontal_border = format!(
            "{}{}{}",
            borders.tl,
            borders.t.repeat(width + padding * 2),
            borders.tr
        );
        let bottom_border = format!(
            "{}{}{}",
            borders.bl,
            borders.b.repeat(width + padding * 2),
            borders.br
        );
        let padding_line = format!(
            "{}{}{}",
            borders.l,
            " ".repeat(width + padding * 2),
            borders.r
        );
        
        let mut result = Vec::new();
        result.push(horizontal_border);
        
        for _ in 0..padding {
            result.push(padding_line.clone());
        }
        
        for line in lines {
            let padded_line = format!(
                "{}{}{}{}{}",
                borders.l,
                " ".repeat(padding),
                format!("{:<width$}", line, width = width),
                " ".repeat(padding),
                borders.r
            );
            result.push(padded_line);
        }
        
        for _ in 0..padding {
            result.push(padding_line.clone());
        }
        
        result.push(bottom_border);
        
        let output = result.join("\n");
        
        if fg_color.is_some() || bg_color.is_some() || style.is_some() {
            Self::colorize(&output, fg_color, bg_color, style)
        } else {
            output
        }
    }

    #[staticmethod]
    fn highlight_text(
        text: &str,
        pattern: &str,
        fg_color: Option<u8>,
        bg_color: Option<u8>,
        style: Option<u8>,
        case_sensitive: Option<bool>,
    ) -> String {
        let case_sensitive = case_sensitive.unwrap_or(false);
        
        if pattern.is_empty() {
            return text.to_string();
        }
        
        let highlighted = Self::colorize(pattern, fg_color, bg_color, style);
        
        if case_sensitive {
            text.replace(pattern, &highlighted)
        } else {
            let lower_text = text.to_lowercase();
            let lower_pattern = pattern.to_lowercase();
            
            let mut result = String::new();
            let mut last_idx = 0;
            
            for (idx, _) in lower_text.match_indices(&lower_pattern) {
                result.push_str(&text[last_idx..idx]);
                let original = &text[idx..idx + pattern.len()];
                result.push_str(&Self::colorize(original, fg_color, bg_color, style));
                last_idx = idx + pattern.len();
            }
            result.push_str(&text[last_idx..]);
            
            result
        }
    }

    #[staticmethod]
    fn random_color(text: &str, style: Option<u8>) -> String {
        use std::collections::hash_map::RandomState;
        use std::hash::{BuildHasher, Hash, Hasher};
        
        let hasher = RandomState::new();
        let mut h = hasher.build_hasher();
        text.hash(&mut h);
        let hash = h.finish();
        
        let r = ((hash >> 16) & 0xFF) as u8;
        let g = ((hash >> 8) & 0xFF) as u8;
        let b = (hash & 0xFF) as u8;
        
        Self::rgb(text, r, g, b, None, style)
    }

    #[staticmethod]
    fn random_bg(text: &str, style: Option<u8>) -> String {
        use std::collections::hash_map::RandomState;
        use std::hash::{BuildHasher, Hash, Hasher};
        
        let hasher = RandomState::new();
        let mut h = hasher.build_hasher();
        text.hash(&mut h);
        let hash = h.finish();
        
        let bg_r = ((hash >> 16) & 0xFF) as u8;
        let bg_g = ((hash >> 8) & 0xFF) as u8;
        let bg_b = (hash & 0xFF) as u8;
        
        let luminance = (0.299 * bg_r as f64 + 0.587 * bg_g as f64 + 0.114 * bg_b as f64) / 255.0;
        let (fg_r, fg_g, fg_b) = if luminance > 0.5 {
            (0, 0, 0)
        } else {
            (255, 255, 255)
        };
        
        Self::rgb_bg(text, bg_r, bg_g, bg_b, Some(fg_r), Some(fg_g), Some(fg_b), style)
    }

    #[staticmethod]
    fn multi_color_text(text: &str, color_map: HashMap<String, (u8, u8, u8)>) -> String {
        let mut result = text.to_string();
        
        for (substring, (r, g, b)) in color_map {
            if result.contains(&substring) {
                let colored = Self::rgb(&substring, r, g, b, None, None);
                result = result.replace(&substring, &colored);
            }
        }
        
        result
    }

    // NEW FEATURE: Batch colorization for better performance
    #[staticmethod]
    fn batch_colorize(texts: Vec<String>, r: u8, g: u8, b: u8) -> Vec<String> {
        texts
            .into_iter()
            .map(|text| Self::rgb(&text, r, g, b, None, None))
            .collect()
    }

    // NEW FEATURE: Strip all ANSI codes from text
    #[staticmethod]
    fn strip_ansi(text: &str) -> String {
        let re = regex::Regex::new(r"\x1b\[[0-9;]*m").unwrap();
        re.replace_all(text, "").to_string()
    }

    // NEW FEATURE: Get visible length (excluding ANSI codes)
    #[staticmethod]
    fn visible_length(text: &str) -> usize {
        Self::strip_ansi(text).len()
    }

    // NEW FEATURE: Wrap text with color
    #[staticmethod]
    fn wrap_colored(
        text: &str,
        width: usize,
        r: u8,
        g: u8,
        b: u8,
        indent: Option<usize>,
    ) -> Vec<String> {
        let indent_size = indent.unwrap_or(0);
        let indent_str = " ".repeat(indent_size);
        let mut lines = Vec::new();
        let words: Vec<&str> = text.split_whitespace().collect();
        let mut current_line = String::new();
        
        for word in words {
            if current_line.len() + word.len() + 1 > width {
                if !current_line.is_empty() {
                    lines.push(format!("{}{}", indent_str, Self::rgb(&current_line.trim(), r, g, b, None, None)));
                    current_line.clear();
                }
            }
            current_line.push_str(word);
            current_line.push(' ');
        }
        
        if !current_line.is_empty() {
            lines.push(format!("{}{}", indent_str, Self::rgb(&current_line.trim(), r, g, b, None, None)));
        }
        
        lines
    }

    // NEW FEATURE: Create a color palette visualization
    #[staticmethod]
    fn show_palette(palette_type: Option<&str>) -> String {
        let palette = palette_type.unwrap_or("basic");
        let mut result = String::new();
        
        match palette {
            "basic" => {
                result.push_str("Basic Colors:\n");
                for i in 30..38 {
                    result.push_str(&format!("{} ", Self::colorize("██", Some(i), None, None)));
                }
                result.push_str("\n");
            }
            "256" => {
                result.push_str("256 Color Palette:\n");
                for i in 0..=255 {
                    result.push_str(&Self::color256("█", i, None, None));
                    if (i + 1) % 16 == 0 {
                        result.push('\n');
                    }
                }
            }
            "rgb" => {
                result.push_str("RGB Spectrum Sample:\n");
                for r in (0..=255).step_by(51) {
                    for g in (0..=255).step_by(51) {
                        for b in (0..=255).step_by(51) {
                            result.push_str(&Self::rgb("█", r as u8, g as u8, b as u8, None, None));
                        }
                        result.push('\n');
                    }
                }
            }
            _ => {
                result = "Unknown palette type. Use 'basic', '256', or 'rgb'".to_string();
            }
        }
        
        result
    }

    // NEW FEATURE: Interpolate between two colors
    #[staticmethod]
    fn interpolate_colors(
        color1: (u8, u8, u8),
        color2: (u8, u8, u8),
        steps: usize,
    ) -> Vec<(u8, u8, u8)> {
        let mut colors = Vec::new();
        
        for i in 0..steps {
            let ratio = i as f64 / (steps - 1).max(1) as f64;
            let r = (color1.0 as f64 + (color2.0 as i16 - color1.0 as i16) as f64 * ratio) as u8;
            let g = (color1.1 as f64 + (color2.1 as i16 - color1.1 as i16) as f64 * ratio) as u8;
            let b = (color1.2 as f64 + (color2.2 as i16 - color1.2 as i16) as f64 * ratio) as u8;
            colors.push((r, g, b));
        }
        
        colors
    }
}

// Helper structures
struct BorderChars {
    tl: String,
    t: String,
    tr: String,
    l: String,
    r: String,
    ml: String,
    m: String,
    mr: String,
    bl: String,
    b: String,
    br: String,
}

fn get_border_chars(style: &str) -> BorderChars {
    match style {
        "double" => BorderChars {
            tl: "╔".to_string(),
            t: "═".to_string(),
            tr: "╗".to_string(),
            l: "║".to_string(),
            r: "║".to_string(),
            ml: "╠".to_string(),
            m: "═".to_string(),
            mr: "╣".to_string(),
            bl: "╚".to_string(),
            b: "═".to_string(),
            br: "╝".to_string(),
        },
        "rounded" => BorderChars {
            tl: "╭".to_string(),
            t: "─".to_string(),
            tr: "╮".to_string(),
            l: "│".to_string(),
            r: "│".to_string(),
            ml: "├".to_string(),
            m: "─".to_string(),
            mr: "┤".to_string(),
            bl: "╰".to_string(),
            b: "─".to_string(),
            br: "╯".to_string(),
        },
        "bold" => BorderChars {
            tl: "┏".to_string(),
            t: "━".to_string(),
            tr: "┓".to_string(),
            l: "┃".to_string(),
            r: "┃".to_string(),
            ml: "┣".to_string(),
            m: "━".to_string(),
            mr: "┫".to_string(),
            bl: "┗".to_string(),
            b: "━".to_string(),
            br: "┛".to_string(),
        },
        "dashed" => BorderChars {
            tl: "┌".to_string(),
            t: "┄".to_string(),
            tr: "┐".to_string(),
            l: "┆".to_string(),
            r: "┆".to_string(),
            ml: "├".to_string(),
            m: "┄".to_string(),
            mr: "┤".to_string(),
            bl: "└".to_string(),
            b: "┄".to_string(),
            br: "┘".to_string(),
        },
        _ => BorderChars {
            tl: "┌".to_string(),
            t: "─".to_string(),
            tr: "┐".to_string(),
            l: "│".to_string(),
            r: "│".to_string(),
            ml: "├".to_string(),
            m: "─".to_string(),
            mr: "┤".to_string(),
            bl: "└".to_string(),
            b: "─".to_string(),
            br: "┘".to_string(),
        },
    }
}

struct Theme {
    fg: (u8, u8, u8),
    bg: (u8, u8, u8),
    style: Option<u8>,
}

fn get_theme_presets() -> HashMap<String, Theme> {
    let mut themes = HashMap::new();
    
    themes.insert("matrix".to_string(), Theme {
        fg: (0, 255, 0),
        bg: (0, 0, 0),
        style: Some(BOLD),
    });
    
    themes.insert("ocean".to_string(), Theme {
        fg: (0, 191, 255),
        bg: (0, 0, 139),
        style: None,
    });
    
    themes.insert("sunset".to_string(), Theme {
        fg: (255, 165, 0),
        bg: (178, 34, 34),
        style: None,
    });
    
    themes.insert("forest".to_string(), Theme {
        fg: (34, 139, 34),
        bg: (0, 100, 0),
        style: None,
    });
    
    themes.insert("neon".to_string(), Theme {
        fg: (255, 0, 255),
        bg: (0, 0, 0),
        style: Some(BOLD),
    });
    
    themes.insert("pastel".to_string(), Theme {
        fg: (255, 192, 203),
        bg: (230, 230, 250),
        style: None,
    });
    
    themes.insert("retro".to_string(), Theme {
        fg: (255, 165, 0),
        bg: (0, 0, 0),
        style: Some(BOLD),
    });
    
    themes.insert("cyberpunk".to_string(), Theme {
        fg: (0, 255, 255),
        bg: (139, 0, 139),
        style: Some(BOLD),
    });
    
    themes.insert("desert".to_string(), Theme {
        fg: (210, 180, 140),
        bg: (244, 164, 96),
        style: None,
    });
    
    themes.insert("dracula".to_string(), Theme {
        fg: (248, 248, 242),
        bg: (40, 42, 54),
        style: None,
    });
    
    themes
}

fn get_color_presets() -> HashMap<String, (u8, u8, u8)> {
    let mut presets = HashMap::new();
    
    presets.insert("forest_green".to_string(), (34, 139, 34));
    presets.insert("sky_blue".to_string(), (135, 206, 235));
    presets.insert("coral".to_string(), (255, 127, 80));
    presets.insert("gold".to_string(), (255, 215, 0));
    presets.insert("lavender".to_string(), (230, 230, 250));
    presets.insert("tomato".to_string(), (255, 99, 71));
    presets.insert("teal".to_string(), (0, 128, 128));
    presets.insert("salmon".to_string(), (250, 128, 114));
    presets.insert("violet".to_string(), (238, 130, 238));
    presets.insert("khaki".to_string(), (240, 230, 140));
    presets.insert("turquoise".to_string(), (64, 224, 208));
    presets.insert("firebrick".to_string(), (178, 34, 34));
    presets.insert("navy".to_string(), (0, 0, 128));
    presets.insert("steel_blue".to_string(), (70, 130, 180));
    presets.insert("olive".to_string(), (128, 128, 0));
    presets.insert("spring_green".to_string(), (0, 255, 127));
    presets.insert("crimson".to_string(), (220, 20, 60));
    presets.insert("chocolate".to_string(), (210, 105, 30));
    presets.insert("midnight_blue".to_string(), (25, 25, 112));
    presets.insert("orchid".to_string(), (218, 112, 214));
    
    presets
}

#[pymodule]
fn chromin(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<ColoredText>()?;
    
    // Add constants at module level
    m.add("BLACK", BLACK)?;
    m.add("RED", RED)?;
    m.add("GREEN", GREEN)?;
    m.add("YELLOW", YELLOW)?;
    m.add("BLUE", BLUE)?;
    m.add("MAGENTA", MAGENTA)?;
    m.add("CYAN", CYAN)?;
    m.add("WHITE", WHITE)?;
    
    m.add("BRIGHT_BLACK", BRIGHT_BLACK)?;
    m.add("BRIGHT_RED", BRIGHT_RED)?;
    m.add("BRIGHT_GREEN", BRIGHT_GREEN)?;
    m.add("BRIGHT_YELLOW", BRIGHT_YELLOW)?;
    m.add("BRIGHT_BLUE", BRIGHT_BLUE)?;
    m.add("BRIGHT_MAGENTA", BRIGHT_MAGENTA)?;
    m.add("BRIGHT_CYAN", BRIGHT_CYAN)?;
    m.add("BRIGHT_WHITE", BRIGHT_WHITE)?;
    
    m.add("BG_BLACK", BG_BLACK)?;
    m.add("BG_RED", BG_RED)?;
    m.add("BG_GREEN", BG_GREEN)?;
    m.add("BG_YELLOW", BG_YELLOW)?;
    m.add("BG_BLUE", BG_BLUE)?;
    m.add("BG_MAGENTA", BG_MAGENTA)?;
    m.add("BG_CYAN", BG_CYAN)?;
    m.add("BG_WHITE", BG_WHITE)?;
    
    m.add("BG_BRIGHT_BLACK", BG_BRIGHT_BLACK)?;
    m.add("BG_BRIGHT_RED", BG_BRIGHT_RED)?;
    m.add("BG_BRIGHT_GREEN", BG_BRIGHT_GREEN)?;
    m.add("BG_BRIGHT_YELLOW", BG_BRIGHT_YELLOW)?;
    m.add("BG_BRIGHT_BLUE", BG_BRIGHT_BLUE)?;
    m.add("BG_BRIGHT_MAGENTA", BG_BRIGHT_MAGENTA)?;
    m.add("BG_BRIGHT_CYAN", BG_BRIGHT_CYAN)?;
    m.add("BG_BRIGHT_WHITE", BG_BRIGHT_WHITE)?;
    
    m.add("BOLD", BOLD)?;
    m.add("DIM", DIM)?;
    m.add("ITALIC", ITALIC)?;
    m.add("UNDERLINE", UNDERLINE)?;
    m.add("BLINK", BLINK)?;
    m.add("RAPID_BLINK", RAPID_BLINK)?;
    m.add("REVERSE", REVERSE)?;
    m.add("HIDDEN", HIDDEN)?;
    m.add("STRIKETHROUGH", STRIKETHROUGH)?;
    m.add("RESET", RESET)?;
    
    Ok(())
}
