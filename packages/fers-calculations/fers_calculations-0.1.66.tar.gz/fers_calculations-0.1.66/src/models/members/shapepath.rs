use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

use crate::models::members::shapecommand::ShapeCommand;

#[derive(Serialize, Deserialize, ToSchema, Debug, Clone)]
pub struct ShapePath {
    pub id: u32,
    pub name: String,
    pub shape_commands: Vec<ShapeCommand>,
}
