use std::collections::HashMap;

use serde::{Deserialize, Serialize};
use serde_json::Value;

use super::source::NotebookSource;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
pub struct Notebook {
    pub name: Option<String>,
    pub title: String,
    #[serde(rename = "notebookId", skip_serializing_if = "Option::is_none")]
    pub notebook_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub emoji: Option<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub sources: Vec<NotebookSource>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<NotebookMetadata>,
    #[serde(flatten)]
    pub extra: HashMap<String, Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NotebookRef {
    pub notebook_id: String,
    pub name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
pub struct NotebookMetadata {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub create_time: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub is_shareable: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub is_shared: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub last_viewed: Option<String>,
    #[serde(flatten)]
    pub extra: HashMap<String, Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BatchDeleteNotebooksRequest {
    pub names: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BatchDeleteNotebooksResponse {
    #[serde(flatten)]
    pub extra: HashMap<String, Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
pub struct ListRecentlyViewedResponse {
    #[serde(default)]
    pub notebooks: Vec<Notebook>,
}
