# nvim-plugin-api

The API for getting information about  nvim-plugins.

## Routes

The list of routes the API should supply:

#### 1. List of Plugins

- **Endpoint**: `/api/plugins`
- **Method**: `GET`
- **Returns**: List of plugins with basic information.

#### 2. Plugin Details

- **Endpoint**: `/api/plugins/{plugin_id}`
- **Method**: `GET`
- **Returns**: Detailed information about a specific plugin.

#### 3. Search

- **Endpoint**: `/api/plugins/search`
- **Method**: `GET`
- **Query Parameters**: `query` (search keyword)
- **Returns**: List of plugins that match the search criteria.

### 4. (Optional) Trending

- **Endpoint**: `/api/plugins/trending`
- **Method**: `GET`
- **Returns**: List of plugins that are trending recently (requires tracking of stars/commits).
