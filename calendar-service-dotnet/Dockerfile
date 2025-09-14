FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["*.csproj", "./"]
RUN dotnet restore "./*.csproj"
COPY . .
WORKDIR "/src/."
RUN dotnet build "CalendarService.DotNet.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "CalendarService.DotNet.csproj" -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "CalendarService.DotNet.dll"]