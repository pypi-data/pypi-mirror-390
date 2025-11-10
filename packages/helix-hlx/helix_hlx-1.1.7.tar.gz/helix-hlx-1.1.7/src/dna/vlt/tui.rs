use crate::dna::vlt::{Manifest, Vault, VaultError, Version};
use chrono::Local;
use crossterm::cursor::{Hide, Show};
use crossterm::event::{self, Event, KeyCode, KeyEvent, KeyModifiers};
use crossterm::execute;
use crossterm::terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen};
use ratatui::backend::CrosstermBackend;
use ratatui::layout::{Constraint, Direction, Layout, Rect};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, List, ListItem, ListState, Paragraph, Tabs};
use ratatui::Terminal;
use std::collections::VecDeque;
use std::fs;
use std::io;
use std::path::Path;
use std::time::{Duration, Instant};
use sha2::{Digest, Sha256};
use thiserror::Error;

pub type TuiResult<T> = Result<T, TuiError>;

#[derive(Debug, Error)]
pub enum TuiError {
    #[error("terminal error: {0}")]
    Io(#[from] io::Error),
    #[error("vault error: {0}")]
    Vault(#[from] VaultError),
    #[error("serialization error: {0}")]
    Serde(#[from] serde_json::Error),
    #[error("utf8 error: {0}")]
    Utf8(#[from] std::string::FromUtf8Error),
    #[error("tui error: {0}")]
    Other(String),
}

pub fn launch() -> TuiResult<()> {
    enable_raw_mode()?;
    execute!(io::stdout(), EnterAlternateScreen, Hide)?;

    let backend = CrosstermBackend::new(io::stdout());
    let mut terminal = Terminal::new(backend)?;
    terminal.clear()?;

    let result = run_app(&mut terminal);

    disable_raw_mode().ok();
    execute!(terminal.backend_mut(), LeaveAlternateScreen, Show).ok();
    terminal.show_cursor().ok();

    result
}

fn run_app(terminal: &mut Terminal<CrosstermBackend<io::Stdout>>) -> TuiResult<()> {
    let mut app = AppState::new()?;
    let mut last_tick = Instant::now();
    let tick_rate = Duration::from_millis(250);

    loop {
        terminal.draw(|f| render_ui(f, &app))?;

        let timeout = tick_rate
            .checked_sub(last_tick.elapsed())
            .unwrap_or_else(|| Duration::from_secs(0));

        if event::poll(timeout)? {
            if let Event::Key(key) = event::read()? {
                handle_key_event(&mut app, key)?;
            }
        }

        if last_tick.elapsed() >= tick_rate {
            app.on_tick();
            last_tick = Instant::now();
        }

        if app.should_quit {
            break;
        }
    }

    Ok(())
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FocusArea {
    Files,
    Tabs,
    Editor,
    Operators,
    Commands,
    Terminal,
    Status,
}

#[derive(Clone)]
struct FileEntry {
    display_name: String,
    original_path: Option<String>,
    hash: String,
    latest_version: Option<Version>,
    version_count: usize,
}

#[derive(Clone)]
struct OperatorCategory {
    key: char,
    name: &'static str,
    operators: &'static [OperatorItem],
}

#[derive(Clone, Copy)]
struct OperatorItem {
    ident: &'static str,
    description: &'static str,
}

#[derive(Clone)]
struct CommandItem {
    title: &'static str,
    shortcut: &'static str,
}

#[derive(Clone)]
struct DocumentTab {
    title: String,
    content: String,
    bound_hash: Option<String>,
    bound_version: Option<String>,
    original_path: Option<String>,
    dirty: bool,
}

pub struct AppState {
    focus: FocusArea,
    should_quit: bool,
    vault: Vault,
    files: Vec<FileEntry>,
    file_list_state: ListState,
    operator_categories: Vec<OperatorCategory>,
    operator_category_index: usize,
    operator_list_state: ListState,
    operator_selection_per_category: Vec<usize>,
    commands: Vec<CommandItem>,
    command_state: ListState,
    tabs: Vec<DocumentTab>,
    active_tab: usize,
    logs: VecDeque<String>,
}

impl AppState {
    pub fn new() -> TuiResult<Self> {
        let vault = Vault::new()?;
        let files = load_vault_files(&vault)?;
        let mut file_list_state = ListState::default();
        if !files.is_empty() {
            file_list_state.select(Some(0));
        }

        let operator_categories = build_operator_catalog();
        let operator_selection_per_category = operator_categories
            .iter()
            .map(|cat| if cat.operators.is_empty() { 0 } else { 0 })
            .collect::<Vec<_>>();

        let mut operator_list_state = ListState::default();
        if let Some(first_cat) = operator_categories.first() {
            if !first_cat.operators.is_empty() {
                operator_list_state.select(Some(0));
            }
        }

        let commands = build_command_list();
        let mut command_state = ListState::default();
        if !commands.is_empty() {
            command_state.select(Some(0));
        }

        let mut tabs = Vec::new();
        if let Some(file) = files.first() {
            let content = load_file_preview(&vault, file)?;
            tabs.push(DocumentTab {
                title: file.display_name.clone(),
                content,
                bound_hash: Some(file.hash.clone()),
                bound_version: file
                    .latest_version
                    .as_ref()
                    .map(|v| v.id.clone()),
                original_path: file.original_path.clone(),
                dirty: false,
            });
        } else {
            tabs.push(DocumentTab {
                title: "untitled".to_string(),
                content: "// Vault empty — press Ctrl+N to create a scratch buffer".to_string(),
                bound_hash: None,
                bound_version: None,
                original_path: None,
                dirty: false,
            });
        }

        let mut app = Self {
            focus: FocusArea::Files,
            should_quit: false,
            vault,
            files,
            file_list_state,
            operator_categories,
            operator_category_index: 0,
            operator_list_state,
            operator_selection_per_category,
            commands,
            command_state,
            tabs,
            active_tab: 0,
            logs: VecDeque::with_capacity(256),
        };

        app.push_log("Helix Vault TUI ready. Ctrl+Q to exit.".to_string());
        Ok(app)
    }

    fn push_log(&mut self, message: String) {
        if self.logs.len() >= 200 {
            self.logs.pop_front();
        }
        self.logs.push_back(message);
    }

    pub fn focus(&mut self, area: FocusArea) {
        self.focus = area;
    }

    pub fn select_next_file(&mut self) {
        if self.files.is_empty() {
            return;
        }
        let idx = self.file_list_state.selected().unwrap_or(0);
        let next = (idx + 1).min(self.files.len() - 1);
        self.file_list_state.select(Some(next));
    }

    pub fn select_prev_file(&mut self) {
        if self.files.is_empty() {
            return;
        }
        let idx = self.file_list_state.selected().unwrap_or(0);
        let prev = idx.saturating_sub(1);
        self.file_list_state.select(Some(prev));
    }

    pub fn open_selected_file(&mut self) -> TuiResult<()> {
        if self.files.is_empty() {
            return Ok(());
        }
        if let Some(idx) = self.file_list_state.selected() {
            let file = self.files.get(idx).cloned();
            if let Some(entry) = file {
                let content = load_file_preview(&self.vault, &entry)?;
                if let Some(tab) = self.tabs.get_mut(self.active_tab) {
                    tab.title = entry.display_name.clone();
                    tab.content = content;
                    tab.bound_hash = Some(entry.hash.clone());
                    tab.bound_version = entry
                        .latest_version
                        .as_ref()
                        .map(|v| v.id.clone());
                    tab.original_path = entry.original_path.clone();
                    tab.dirty = false;
                }
                self.push_log(format!("Opened {}", entry.display_name));
            }
        }
        Ok(())
    }

    fn operator_items(&self) -> &[OperatorItem] {
        self.operator_categories
            .get(self.operator_category_index)
            .map(|cat| cat.operators)
            .unwrap_or_default()
    }

    pub fn select_next_operator(&mut self) {
        let operators = self.operator_items();
        if operators.is_empty() {
            return;
        }
        let idx = self.operator_selection_per_category[self.operator_category_index];
        let next = (idx + 1).min(operators.len() - 1);
        self.operator_selection_per_category[self.operator_category_index] = next;
        self.operator_list_state.select(Some(next));
    }

    pub fn select_prev_operator(&mut self) {
        let operators = self.operator_items();
        if operators.is_empty() {
            return;
        }
        let idx = self.operator_selection_per_category[self.operator_category_index];
        let prev = idx.saturating_sub(1);
        self.operator_selection_per_category[self.operator_category_index] = prev;
        self.operator_list_state.select(Some(prev));
    }

    pub fn cycle_operator_category_next(&mut self) {
        if self.operator_categories.is_empty() {
            return;
        }
        self.operator_category_index = (self.operator_category_index + 1) % self.operator_categories.len();
        self.sync_operator_selection();
        let cat = &self.operator_categories[self.operator_category_index];
        self.push_log(format!("Operator category → {}", cat.name));
    }

    pub fn cycle_operator_category_prev(&mut self) {
        if self.operator_categories.is_empty() {
            return;
        }
        if self.operator_category_index == 0 {
            self.operator_category_index = self.operator_categories.len() - 1;
        } else {
            self.operator_category_index -= 1;
        }
        self.sync_operator_selection();
        let cat = &self.operator_categories[self.operator_category_index];
        self.push_log(format!("Operator category → {}", cat.name));
    }

    pub fn reset_operator_category(&mut self) {
        if self.operator_categories.is_empty() {
            return;
        }
        self.operator_category_index = 0;
        self.sync_operator_selection();
        let cat = &self.operator_categories[self.operator_category_index];
        self.push_log(format!("Operator category → {}", cat.name));
    }

    pub fn sync_operator_selection(&mut self) {
        let index = self.operator_selection_per_category[self.operator_category_index];
        if self.operator_items().is_empty() {
            self.operator_list_state.select(None);
        } else {
            let bounded = index.min(self.operator_items().len() - 1);
            self.operator_selection_per_category[self.operator_category_index] = bounded;
            self.operator_list_state.select(Some(bounded));
        }
    }

    pub fn insert_selected_operator(&mut self) {
        let Some(tab) = self.tabs.get_mut(self.active_tab) else {
            return;
        };

        let category_index = self.operator_category_index;
        let operator_index = self.operator_selection_per_category[category_index];
        let operators = self.operator_categories
            .get(category_index)
            .map(|cat| cat.operators)
            .unwrap_or_default();
        
        if operators.is_empty() {
            return;
        }
        
        let operator = &operators[operator_index];
        let operator_ident = operator.ident.to_string();
        tab.content.push_str(&format!("\n// Using {}\n{} \"example\"", operator_ident, operator_ident));
        tab.dirty = true;
        self.push_log(format!("Inserted operator {}", operator_ident));
    }

    pub fn next_tab(&mut self) {
        if self.tabs.is_empty() {
            return;
        }
        self.active_tab = (self.active_tab + 1) % self.tabs.len();
        self.push_log(format!("Active tab → {}", self.tabs[self.active_tab].title));
    }

    pub fn previous_tab(&mut self) {
        if self.tabs.is_empty() {
            return;
        }
        if self.active_tab == 0 {
            self.active_tab = self.tabs.len() - 1;
        } else {
            self.active_tab -= 1;
        }
        self.push_log(format!("Active tab → {}", self.tabs[self.active_tab].title));
    }

    pub fn close_active_tab(&mut self) {
        if self.tabs.len() <= 1 {
            self.push_log("Cannot close last tab.".to_string());
            return;
        }
        let removed = self.tabs.remove(self.active_tab);
        if self.active_tab >= self.tabs.len() {
            self.active_tab = self.tabs.len() - 1;
        }
        self.push_log(format!("Closed tab {}", removed.title));
    }

    pub fn create_new_tab(&mut self) {
        let title = format!("scratch-{}", self.tabs.len() + 1);
        self.tabs.push(DocumentTab {
            title: title.clone(),
            content: "// New scratch buffer".to_string(),
            bound_hash: None,
            bound_version: None,
            original_path: None,
            dirty: true,
        });
        self.active_tab = self.tabs.len() - 1;
        self.push_log(format!("Created {}", title));
    }

    pub fn save_active_tab(&mut self) -> TuiResult<()> {
        if let Some(tab) = self.tabs.get_mut(self.active_tab) {
            let timestamp = Local::now().format("%Y%m%d%H%M%S");
            let tmp_path = self
                .vault
                .root
                .join("tmp")
                .join(format!("tui_save_{}.hlx", timestamp));
            fs::write(&tmp_path, tab.content.as_bytes())?;
            let version_id = self
                .vault
                .save(&tmp_path, Some("Saved from TUI".to_string()))?;
            let mut hasher = Sha256::new();
            let bytes = fs::read(&tmp_path)?;
            hasher.update(&bytes);
            let hash = format!("{:x}", hasher.finalize());
            tab.bound_hash = Some(hash);
            tab.bound_version = Some(version_id);
            tab.dirty = false;
            self.push_log(format!("Saved buffer → {}", tmp_path.display()));
        }
        Ok(())
    }

    pub fn trigger_command(&mut self) {
        if let Some(idx) = self.command_state.selected() {
            if let Some(cmd) = self.commands.get(idx) {
                self.push_log(format!("Command triggered: {}", cmd.title));
            }
        }
    }

    pub fn select_next_command(&mut self) {
        if self.commands.is_empty() {
            return;
        }
        let idx = self.command_state.selected().unwrap_or(0);
        let next = (idx + 1).min(self.commands.len() - 1);
        self.command_state.select(Some(next));
    }

    pub fn select_prev_command(&mut self) {
        if self.commands.is_empty() {
            return;
        }
        let idx = self.command_state.selected().unwrap_or(0);
        let prev = idx.saturating_sub(1);
        self.command_state.select(Some(prev));
    }

    pub fn on_tick(&mut self) {
        // Currently nothing periodic; placeholder for future status updates.
    }
}

fn handle_editor_keys(app: &mut AppState, key: KeyEvent) {
    // Basic editor key handling - for now just log the key press
    match key.code {
        KeyCode::Char(c) => {
            if let Some(tab) = app.tabs.get_mut(app.active_tab) {
                tab.content.push(c);
                tab.dirty = true;
            }
        }
        KeyCode::Backspace => {
            if let Some(tab) = app.tabs.get_mut(app.active_tab) {
                tab.content.pop();
                tab.dirty = true;
            }
        }
        KeyCode::Enter => {
            if let Some(tab) = app.tabs.get_mut(app.active_tab) {
                tab.content.push('\n');
                tab.dirty = true;
            }
        }
        KeyCode::Tab => {
            if let Some(tab) = app.tabs.get_mut(app.active_tab) {
                tab.content.push_str("    ");
                tab.dirty = true;
            }
        }
        _ => {}
    }
}

fn handle_key_event(app: &mut AppState, key: KeyEvent) -> TuiResult<()> {
    if key.modifiers.contains(KeyModifiers::CONTROL) {
        match key.code {
            KeyCode::Char(c) => {
                let lower = c.to_ascii_lowercase();
                match lower {
                    '1' => app.focus(FocusArea::Files),
                    '2' => app.focus(FocusArea::Tabs),
                    '3' => app.focus(FocusArea::Editor),
                    '4' => app.focus(FocusArea::Operators),
                    '5' => app.focus(FocusArea::Commands),
                    '6' => app.focus(FocusArea::Terminal),
                    '7' => app.focus(FocusArea::Status),
                    'n' => app.create_new_tab(),
                    's' => {
                        if let Err(err) = app.save_active_tab() {
                            app.push_log(format!("Save failed: {}", err));
                        }
                    }
                    't' => app.next_tab(),
                    'x' => app.close_active_tab(),
                    'y' => app.insert_selected_operator(),
                    'a' => app.cycle_operator_category_prev(),
                    'b' => app.cycle_operator_category_next(),
                    'c' => app.reset_operator_category(),
                    'z' => app.push_log("Undo not implemented yet.".to_string()),
                    'q' => app.should_quit = true,
                    _ => {}
                }
            }
            _ => {}
        }
        return Ok(());
    }

    match app.focus {
        FocusArea::Files => match key.code {
            KeyCode::Up => app.select_prev_file(),
            KeyCode::Down => app.select_next_file(),
            KeyCode::Enter => {
                app.open_selected_file()?;
            }
            _ => {}
        },
        FocusArea::Editor => handle_editor_keys(app, key),
        FocusArea::Operators => match key.code {
            KeyCode::Up => app.select_prev_operator(),
            KeyCode::Down => app.select_next_operator(),
            KeyCode::Left => app.cycle_operator_category_prev(),
            KeyCode::Right => app.cycle_operator_category_next(),
            KeyCode::Enter => app.insert_selected_operator(),
            _ => {}
        },
        FocusArea::Commands => match key.code {
            KeyCode::Up => app.select_prev_command(),
            KeyCode::Down => app.select_next_command(),
            KeyCode::Enter => app.trigger_command(),
            _ => {}
        },
        FocusArea::Tabs => match key.code {
            KeyCode::Left => app.previous_tab(),
            KeyCode::Right => app.next_tab(),
            _ => {}
        },
        FocusArea::Terminal | FocusArea::Status => {
            if key.code == KeyCode::Esc {
                app.should_quit = true;
            }
        }
    }

    Ok(())
}

fn render_ui(frame: &mut ratatui::Frame, app: &AppState) {
    let size = frame.size();

    let vertical_chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Min(10),
            Constraint::Length(8),
            Constraint::Length(1),
        ])
        .split(size);

    let body_chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Length(28),
            Constraint::Min(40),
            Constraint::Length(34),
        ])
        .split(vertical_chunks[0]);

    render_files(frame, body_chunks[0], app);
    render_editor(frame, body_chunks[1], app);
    render_side_panel(frame, body_chunks[2], app);
    render_terminal(frame, vertical_chunks[1], app);
    render_status(frame, vertical_chunks[2], app);
}

fn render_files(frame: &mut ratatui::Frame, area: Rect, app: &AppState) {
    let items: Vec<ListItem> = app
        .files
        .iter()
        .map(|file| {
            let info = file
                .latest_version
                .as_ref()
                .map(|version| {
                    let local_time = version
                        .created_at
                        .with_timezone(&Local)
                        .format("%Y-%m-%d %H:%M");
                    format!("{} · {} versions", local_time, file.version_count)
                })
                .unwrap_or_else(|| format!("{} versions", file.version_count));

            let spans = vec![
                Line::from(Span::styled(
                    file.display_name.clone(),
                    Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD),
                )),
                Line::from(Span::raw(info)),
            ];
            ListItem::new(spans)
        })
        .collect();

    let focused = app.focus == FocusArea::Files;
    let title = if focused { "Files (Ctrl+1) *" } else { "Files (Ctrl+1)" };
    let block = Block::default()
        .borders(Borders::ALL)
        .title(Line::from(vec![Span::styled(
            title,
            Style::default().fg(if focused { Color::Cyan } else { Color::Gray }),
        )]));

    let list = List::new(items)
        .block(block)
        .highlight_style(Style::default().bg(Color::DarkGray).fg(Color::White))
        .highlight_symbol("▶ ");

    frame.render_stateful_widget(list, area, &mut app.file_list_state.clone());
}

fn render_editor(frame: &mut ratatui::Frame, area: Rect, app: &AppState) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Length(3), Constraint::Min(5)])
        .split(area);

    let titles: Vec<Line> = app
        .tabs
        .iter()
        .map(|tab| {
            let mut display = tab.title.clone();
            if tab.dirty {
                display.push('*');
            }
            Line::from(Span::raw(display))
        })
        .collect();
    let tabs = Tabs::new(titles)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title(if app.focus == FocusArea::Tabs {
                    Line::from(Span::styled("Tabs (Ctrl+2) *", Style::default().fg(Color::Cyan)))
                } else {
                    Line::from(Span::styled("Tabs (Ctrl+2)", Style::default().fg(Color::Gray)))
                }),
        )
        .select(app.active_tab)
        .highlight_style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD));
    frame.render_widget(tabs, chunks[0]);

    let content = app
        .tabs
        .get(app.active_tab)
        .map(|tab| tab.content.clone())
        .unwrap_or_else(|| "".to_string());

    let block_title = if app.focus == FocusArea::Editor {
        "Document (Ctrl+3)"
    } else {
        "Document"
    };

    let paragraph = Paragraph::new(content)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title(block_title)
                .border_style(if app.focus == FocusArea::Editor {
                    Style::default().fg(Color::Cyan)
                } else {
                    Style::default()
                }),
        );

    frame.render_widget(paragraph, chunks[1]);
}

fn render_side_panel(frame: &mut ratatui::Frame, area: Rect, app: &AppState) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Length(10), Constraint::Min(5)])
        .split(area);

    render_command_panel(frame, chunks[0], app);
    render_operator_panel(frame, chunks[1], app);
}

fn render_command_panel(frame: &mut ratatui::Frame, area: Rect, app: &AppState) {
    let items: Vec<ListItem> = app
        .commands
        .iter()
        .map(|cmd| {
            let line = Line::from(vec![
                Span::styled(cmd.title, Style::default().fg(Color::White)),
                Span::raw(" "),
                Span::styled(cmd.shortcut, Style::default().fg(Color::DarkGray)),
            ]);
            ListItem::new(line)
        })
        .collect();

    let focused = app.focus == FocusArea::Commands;
    let title = if focused { "Commands (Ctrl+4) *" } else { "Commands (Ctrl+4)" };
    let block = Block::default()
        .borders(Borders::ALL)
        .title(Span::styled(
            title,
            Style::default().fg(if focused { Color::Cyan } else { Color::Gray }),
        ));

    let list = List::new(items)
        .block(block)
        .highlight_style(Style::default().bg(Color::DarkGray).fg(Color::White))
        .highlight_symbol("⚡ ");

    frame.render_stateful_widget(list, area, &mut app.command_state.clone());
}

fn render_operator_panel(frame: &mut ratatui::Frame, area: Rect, app: &AppState) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Length(3), Constraint::Min(3)])
        .split(area);

    let category_titles: Vec<Span> = app
        .operator_categories
        .iter()
        .enumerate()
        .map(|(idx, cat)| {
            let label = format!("[{}] {}", cat.key.to_ascii_uppercase(), cat.name);
            let style = if idx == app.operator_category_index {
                Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::Gray)
            };
            Span::styled(label, style)
        })
        .collect();

    let category_block = Block::default()
        .borders(Borders::ALL)
        .title(if app.focus == FocusArea::Operators {
            Span::styled("Operator Categories (Ctrl+3) *", Style::default().fg(Color::Cyan))
        } else {
            Span::styled("Operator Categories", Style::default().fg(Color::Gray))
        });

    frame.render_widget(
        Paragraph::new(Line::from(category_titles)).block(category_block),
        chunks[0],
    );

    let items: Vec<ListItem> = app
        .operator_items()
        .iter()
        .map(|op| {
            ListItem::new(Line::from(vec![
                Span::styled(op.ident, Style::default().fg(Color::Cyan)),
                Span::raw(" — "),
                Span::styled(op.description, Style::default().fg(Color::Gray)),
            ]))
        })
        .collect();

    let block = Block::default()
        .borders(Borders::ALL)
        .title("Operators (Ctrl+Y to insert)")
        .border_style(if app.focus == FocusArea::Operators {
            Style::default().fg(Color::Cyan)
        } else {
            Style::default()
        });

    let list = List::new(items)
        .block(block)
        .highlight_style(Style::default().bg(Color::DarkGray).fg(Color::White))
        .highlight_symbol("♪ ");

    frame.render_stateful_widget(list, chunks[1], &mut app.operator_list_state.clone());
}

fn render_terminal(frame: &mut ratatui::Frame, area: Rect, app: &AppState) {
    let logs: Vec<ListItem> = app
        .logs
        .iter()
        .rev()
        .map(|line| ListItem::new(Line::from(line.clone())))
        .collect();

    let title = if app.focus == FocusArea::Terminal {
        "Terminal Log (Ctrl+5) *"
    } else {
        "Terminal Log (Ctrl+5)"
    };

    let block = Block::default()
        .borders(Borders::ALL)
        .title(Span::styled(
            title,
            Style::default().fg(if app.focus == FocusArea::Terminal {
                Color::Cyan
            } else {
                Color::Gray
            }),
        ));

    frame.render_widget(List::new(logs).block(block), area);
}

fn render_status(frame: &mut ratatui::Frame, area: Rect, app: &AppState) {
    let focus_label = match app.focus {
        FocusArea::Files => "Files",
        FocusArea::Tabs => "Tabs",
        FocusArea::Editor => "Editor",
        FocusArea::Operators => "Operators",
        FocusArea::Commands => "Commands",
        FocusArea::Terminal => "Terminal",
        FocusArea::Status => "Status",
    };

    let dirty = app
        .tabs
        .get(app.active_tab)
        .map(|tab| if tab.dirty { "dirty" } else { "clean" })
        .unwrap_or("clean");

    let status_line = Line::from(vec![
        Span::styled(" helix>", Style::default().fg(Color::Green)),
        Span::raw(" focus:"),
        Span::styled(focus_label, Style::default().fg(Color::Yellow)),
        Span::raw("  tab:"),
        Span::styled(
            app.tabs
                .get(app.active_tab)
                .map(|tab| tab.title.as_str())
                .unwrap_or("-"),
            Style::default().fg(Color::White),
        ),
        Span::raw("  state:"),
        Span::styled(dirty, Style::default().fg(Color::Magenta)),
        Span::raw("  Ctrl+Q to exit"),
    ]);

    let block = Block::default()
        .borders(Borders::TOP)
        .title(Span::styled(
            "Status (Ctrl+6)",
            Style::default().fg(if app.focus == FocusArea::Status {
                Color::Cyan
            } else {
                Color::DarkGray
            }),
        ));

    frame.render_widget(Paragraph::new(status_line).block(block), area);
}

fn load_vault_files(vault: &Vault) -> TuiResult<Vec<FileEntry>> {
    let mut entries = Vec::new();
    let vlt_dir = vault.root.join("vlt");
    if !vlt_dir.exists() {
        return Ok(entries);
    }

    for entry in fs::read_dir(&vlt_dir)? {
        let entry = entry?;
        if !entry.path().is_dir() {
            continue;
        }
        let manifest_path = entry.path().join("manifest.json");
        if !manifest_path.exists() {
            continue;
        }
        let manifest: Manifest = serde_json::from_str(&fs::read_to_string(&manifest_path)?)?;
        let display_name = manifest
            .original_path
            .as_ref()
            .and_then(|p| Path::new(p).file_name().map(|f| f.to_string_lossy().to_string()))
            .unwrap_or_else(|| manifest.file_hash.clone());

        let latest_version = manifest.versions.last().cloned();
        entries.push(FileEntry {
            display_name,
            original_path: manifest.original_path.clone(),
            hash: manifest.file_hash.clone(),
            latest_version,
            version_count: manifest.versions.len(),
        });
    }

    entries.sort_by(|a, b| a.display_name.cmp(&b.display_name));
    Ok(entries)
}

fn load_file_preview(vault: &Vault, file: &FileEntry) -> TuiResult<String> {
    if let Some(version) = &file.latest_version {
        let bytes = vault.load_version(&file.hash, &version.id)?;
        let preview = String::from_utf8(bytes).unwrap_or_else(|_| "<binary data>".to_string());
        Ok(preview)
    } else {
        Ok("// No versions available".to_string())
    }
}

fn build_command_list() -> Vec<CommandItem> {
    vec![
        CommandItem { title: "Build", shortcut: "Ctrl+B" },
        CommandItem { title: "Compile", shortcut: "Ctrl+K" },
        CommandItem { title: "Run", shortcut: "Ctrl+R" },
        CommandItem { title: "Test", shortcut: "Ctrl+T" },
        CommandItem { title: "Format", shortcut: "Alt+F" },
        CommandItem { title: "Validate", shortcut: "Ctrl+V" },
    ]
}

const VARIABLES_ENV: &[OperatorItem] = &[
    OperatorItem { ident: "@var", description: "Global variables" },
    OperatorItem { ident: "@env", description: "Environment variables" },
    OperatorItem { ident: "@request", description: "Request data" },
    OperatorItem { ident: "@session", description: "Session map" },
    OperatorItem { ident: "@cookie", description: "Cookies" },
    OperatorItem { ident: "@header", description: "HTTP headers" },
    OperatorItem { ident: "@param", description: "Route params" },
    OperatorItem { ident: "@query", description: "Query params" },
];

const TIME_OPERATORS: &[OperatorItem] = &[
    OperatorItem { ident: "@now", description: "Current timestamp" },
    OperatorItem { ident: "@date", description: "Date formatting" },
    OperatorItem { ident: "@time", description: "Time formatting" },
    OperatorItem { ident: "@timestamp", description: "Unix timestamp" },
    OperatorItem { ident: "@timezone", description: "Timezone conversion" },
    OperatorItem { ident: "@format", description: "Format date/time" },
];

const STRING_OPERATORS: &[OperatorItem] = &[
    OperatorItem { ident: "@string", description: "String utils" },
    OperatorItem { ident: "@regex", description: "Regex operations" },
    OperatorItem { ident: "@json", description: "JSON manipulation" },
    OperatorItem { ident: "@base64", description: "Base64 encode/decode" },
    OperatorItem { ident: "@url", description: "URL encode/decode" },
    OperatorItem { ident: "@hash", description: "Hashing" },
    OperatorItem { ident: "@uuid", description: "UUID generator" },
];

const LOGIC_OPERATORS: &[OperatorItem] = &[
    OperatorItem { ident: "@if", description: "Conditional" },
    OperatorItem { ident: "@switch", description: "Switch statement" },
    OperatorItem { ident: "@case", description: "Match case" },
    OperatorItem { ident: "@default", description: "Default branch" },
    OperatorItem { ident: "@and", description: "Logical AND" },
    OperatorItem { ident: "@or", description: "Logical OR" },
    OperatorItem { ident: "@not", description: "Logical NOT" },
];

const MATH_COLLECTIONS: &[OperatorItem] = &[
    OperatorItem { ident: "@math", description: "Math helpers" },
    OperatorItem { ident: "@calc", description: "Calculator" },
    OperatorItem { ident: "@min", description: "Minimum" },
    OperatorItem { ident: "@max", description: "Maximum" },
    OperatorItem { ident: "@avg", description: "Average" },
    OperatorItem { ident: "@sum", description: "Sum" },
    OperatorItem { ident: "@round", description: "Round" },
    OperatorItem { ident: "@array", description: "Array utilities" },
    OperatorItem { ident: "@map", description: "Map collection" },
    OperatorItem { ident: "@filter", description: "Filter collection" },
    OperatorItem { ident: "@sort", description: "Sort collection" },
    OperatorItem { ident: "@join", description: "Join values" },
    OperatorItem { ident: "@split", description: "Split strings" },
    OperatorItem { ident: "@length", description: "Length utility" },
];

const SYSTEM_OPERATORS: &[OperatorItem] = &[
    OperatorItem { ident: "@exec", description: "System execution" },
    OperatorItem { ident: "@validate", description: "Schema validation" },
    OperatorItem { ident: "@schema", description: "Schema builder" },
];

fn build_operator_catalog() -> Vec<OperatorCategory> {
    vec![
        OperatorCategory { key: 'v', name: "Variables & Env", operators: VARIABLES_ENV },
        OperatorCategory { key: 't', name: "Time", operators: TIME_OPERATORS },
        OperatorCategory { key: 's', name: "Strings & Encoding", operators: STRING_OPERATORS },
        OperatorCategory { key: 'l', name: "Logic", operators: LOGIC_OPERATORS },
        OperatorCategory { key: 'm', name: "Math & Collections", operators: MATH_COLLECTIONS },
        OperatorCategory { key: 'x', name: "System", operators: SYSTEM_OPERATORS },
    ]
}

