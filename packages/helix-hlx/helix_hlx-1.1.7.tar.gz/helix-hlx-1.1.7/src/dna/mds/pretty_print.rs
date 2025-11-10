use crate::dna::atp::ast::{HelixAst, AstPrettyPrinter};

pub fn pretty_print(ast: &HelixAst) -> String {
    let mut printer = AstPrettyPrinter::new();
    printer.print(ast)
}

