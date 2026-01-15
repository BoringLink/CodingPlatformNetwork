#!/usr/bin/env python3
"""测试 query_subgraph 查询逻辑"""

import asyncio

from neo4j import AsyncGraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"


async def test():
    driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    async with driver.session() as session:
        node_id = "732ebccf-13f2-4d6f-94da-bba5f682bf9e"

        # 1. 验证节点存在
        r1 = await session.run("MATCH (n {id: $id}) RETURN count(n) as cnt", id=node_id)
        rec = await r1.single()
        print(f"1. Node exists: {rec['cnt']}")

        # 2. 检查关系
        r2 = await session.run(
            """
            MATCH (n {id: $id})-[r]-(other)
            RETURN type(r) as rel_type, labels(other) as other_labels, other.id as other_id
            LIMIT 5
        """,
            id=node_id,
        )
        recs = await r2.data()
        print(f"2. Relationships found: {len(recs)}")
        for r in recs[:3]:
            print(f"   {r}")

        # 3. 完整子图查询（和代码中一样）
        depth = 2
        query = f"""
            MATCH (root {{id: $root_id}})
            CALL {{
              WITH root
              MATCH p = (root)-[*0..{depth}]-(node)
              RETURN p LIMIT 100
            }}
            UNWIND nodes(p) AS n
            WITH DISTINCT n LIMIT 100
            WITH collect(n) AS all_nodes
            WITH all_nodes, [nd IN all_nodes | nd {{.*, id: nd.id, labels: labels(nd)}}] AS nodes
            
            MATCH (a)-[r]-(b)
            WHERE a IN all_nodes AND b IN all_nodes
            WITH r, a, b, nodes
            LIMIT 100
            
            RETURN nodes, collect(r {{.*, id: elementId(r), type: type(r), source: a.id, target: b.id}}) AS rels
        """
        r3 = await session.run(query, root_id=node_id)
        recs = await r3.data()
        if recs:
            nodes = recs[0].get("nodes", [])
            rels = recs[0].get("rels", [])
            print(f"3. Subgraph: {len(nodes)} nodes, {len(rels)} relationships")
            if nodes:
                print(f"   First node id: {nodes[0].get('id')}")
        else:
            print("3. Subgraph: No results")

    await driver.close()


if __name__ == "__main__":
    asyncio.run(test())
