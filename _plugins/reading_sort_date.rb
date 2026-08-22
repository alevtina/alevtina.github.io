Jekyll::Hooks.register :site, :pre_render do |site|
  reading = site.collections["reading"]
  next unless reading

  reading.docs.each do |doc|
    doc.data["sort_date"] = doc.data["date_finished"] || doc.data["date_started"] || doc.data["date"]
  end
end
