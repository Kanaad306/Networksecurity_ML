-- Run this once in the Supabase SQL editor before python push_data.py

create table if not exists network_data (
  id bigint generated always as identity primary key,
  "having_IP_Address" smallint,
  "URL_Length" smallint,
  "Shortining_Service" smallint,
  "having_At_Symbol" smallint,
  "double_slash_redirecting" smallint,
  "Prefix_Suffix" smallint,
  "having_Sub_Domain" smallint,
  "SSLfinal_State" smallint,
  "Domain_registeration_length" smallint,
  "Favicon" smallint,
  "port" smallint,
  "HTTPS_token" smallint,
  "Request_URL" smallint,
  "URL_of_Anchor" smallint,
  "Links_in_tags" smallint,
  "SFH" smallint,
  "Submitting_to_email" smallint,
  "Abnormal_URL" smallint,
  "Redirect" smallint,
  "on_mouseover" smallint,
  "RightClick" smallint,
  "popUpWidnow" smallint,
  "Iframe" smallint,
  "age_of_domain" smallint,
  "DNSRecord" smallint,
  "web_traffic" smallint,
  "Page_Rank" smallint,
  "Google_Index" smallint,
  "Links_pointing_to_page" smallint,
  "Statistical_report" smallint,
  "Result" smallint
);

-- Allow inserts with the publishable key (run this even if the table already exists)
alter table network_data disable row level security;
grant select, insert on table network_data to anon, authenticated;
