async def get_guild_cached(guild_id, client):
    if client.get_guild(guild_id) is None:
        return await client.fetch_guild(guild_id)
    else:
        return client.get_guild(guild_id)
