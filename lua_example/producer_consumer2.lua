function producer()
  return coroutine.create(function()
    while true do
      local x = io.read()
      print('producer:', x)
      send(x)
    end
  end)
end

function consumer(prod)
  while true do
    local x = receive(prod)
    io.write("consumer:", x, "\n")
  end
end

function filter(prod)
  return coroutine.create(function()
    for line = 1, math.huge do
      local x = receive(prod)
      x = string.format("%5d %s", line, x)
      send(x)
    end
  end)
end

function receive(prod)
  local s, v = coroutine.resume(prod)
  return v
end

function send(x)
  coroutine.yield(x)
end

consumer(filter(producer()))
