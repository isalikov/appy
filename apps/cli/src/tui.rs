//! Minimal ratatui application: a centred greeting, `q`/`Esc` to quit.

use std::time::Duration;

use anyhow::Result;
use crossterm::event::{self, Event, KeyCode, KeyEventKind};
use ratatui::{
    DefaultTerminal, Frame,
    layout::{Constraint, Flex, Layout},
    style::Stylize,
    text::Line,
    widgets::{Block, BorderType, Paragraph},
};

use crate::GREETING;

pub fn run() -> Result<()> {
    // `ratatui::run` sets up raw mode / alternate screen and restores the
    // terminal on exit, including on panic.
    ratatui::run(|terminal| App::default().run(terminal))
}

#[derive(Debug, Default)]
struct App {
    exit: bool,
}

impl App {
    fn run(mut self, terminal: &mut DefaultTerminal) -> Result<()> {
        while !self.exit {
            terminal.draw(Self::draw)?;
            self.handle_events()?;
        }
        Ok(())
    }

    fn draw(frame: &mut Frame) {
        let [area] = Layout::vertical([Constraint::Length(5)])
            .flex(Flex::Center)
            .areas(frame.area());
        let [area] = Layout::horizontal([Constraint::Length(40)])
            .flex(Flex::Center)
            .areas(area);

        let block = Block::bordered()
            .border_type(BorderType::Rounded)
            .title(Line::from(" appy ").bold())
            .title_bottom(Line::from(" q to quit ").dim().centered());
        let greeting = Paragraph::new(vec![
            Line::default(),
            Line::from(GREETING).bold().centered(),
        ])
        .block(block);
        frame.render_widget(greeting, area);
    }

    fn handle_events(&mut self) -> Result<()> {
        if !event::poll(Duration::from_millis(250))? {
            return Ok(());
        }
        if let Event::Key(key) = event::read()?
            && key.kind == KeyEventKind::Press
            && matches!(key.code, KeyCode::Char('q') | KeyCode::Esc)
        {
            self.exit = true;
        }
        Ok(())
    }
}
