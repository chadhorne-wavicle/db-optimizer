explain using json
SELECT 
     r_name,
     n_name,
     p_mfgr,
     p_brand,
     p_type,
     sum(ps_availqty * ps_supplycost) as total_partsupplycost,
     sum(p_size) total_partsize,
     avg(p_retailprice) avg_retailprice,
     sum(s_acctbal)
 FROM New_DBOE.New_RETAIL.part part,
    New_DBOE.New_RETAIL.supplier supplier,
    New_DBOE.New_RETAIL.partsupp partsupp,
    New_DBOE.New_RETAIL.nation nation,
    New_DBOE.New_RETAIL.region region
WHERE
     p_partkey = ps_partkey
     AND s_suppkey = ps_suppkey
     AND s_nationkey = n_nationkey
     AND n_regionkey = r_regionkey
     AND p_type like '%COPPER%'
     AND r_name in ('ASIA','AMERICA')
     and n_name not in ('VIETNAM')
group by  r_name,
     n_name,
     p_mfgr,
     p_brand,
     p_type
order by  r_name,
     n_name,
     p_mfgr,
     p_brand,
     p_type 