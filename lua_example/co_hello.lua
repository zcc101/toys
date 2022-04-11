co = coroutine.create(function()
  for i = 1, 10 do
    -- print(i)
    coroutine.yield(i)
  end
end)

print(coroutine.resume(co))
print(coroutine.resume(co))
print(coroutine.resume(co))
print(coroutine.resume(co))
print(coroutine.resume(co))
print(coroutine.resume(co))
